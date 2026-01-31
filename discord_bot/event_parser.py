import re
import os
import json
import sys
from anthropic import Anthropic
from datetime import datetime, timedelta

class EventParser:
    """Parse Discord messages for event scheduling using Claude."""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.conversation_history = []  # For agentic memory
        self.scheduling_examples = []  # Store examples of scheduling patterns

    def llm_check(self, content: str) -> dict | None:
        """
        Use Claude to determine if this is an event scheduling message
        and extract the event details if it is.

        Returns:
            dict with keys: name, location, description, datetime_hint, is_event
            None if LLM decides it's not an event scheduling message
        """
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": f"""Analyze this Discord message to determine if it's someone suggesting, proposing, or trying to schedule a social activity, event, or gathering (including informal plans like getting coffee, lunch, drinks, etc.).

Message: "{content}"

Be inclusive - if there's any mention of wanting to do something social with others or at a specific time, consider it an event.

IMPORTANT: Always generate a meaningful name/title for the activity based on what's mentioned in the message. For example:
- "wanna get coffee" -> name should be "Coffee Meetup" or similar
- "go to mcdonalds" -> name should be "McDonald's Hangout"
- Never return null for name if is_event is true - create a descriptive title from the message content

Respond with a JSON object containing:
- "is_event": boolean (true if this is about planning/suggesting any social activity)
- "name": string (name/title of the activity - REQUIRED if is_event is true, generate from message content)
- "location": string (location mentioned, or null)
- "description": string (brief description of what the activity is, or null)
- "datetime_hint": string (any date/time mentioned, or null)
- "confidence": number (0-1, confidence this is a social activity/event planning message)

Only return valid JSON, no other text."""
            })

            response = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=500,
                messages=self.conversation_history
            )

            response_text = response.content[0].text.strip()

            print(f"Raw Claude response: '{response_text}'", flush=True)

            # Strip markdown code blocks if present
            if response_text.startswith("```"):
                # Remove opening ```json or ```
                response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text
                # Remove closing ```
                if response_text.endswith("```"):
                    response_text = response_text[:-3].rstrip()

            # Add assistant response to history for memory
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content[0].text.strip()  # Store original response
            })

            # Keep conversation history manageable (last 20 exchanges)
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]

            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as je:
                print(f"JSON parsing error: {je}", flush=True)
                print(f"Response was: {response_text}", flush=True)
                return None

            print(f"LLM Response: {result}", flush=True)
            sys.stdout.flush()

            # Only return if confidence is reasonable and it's actually an event
            if result.get('is_event') and result.get('confidence', 0) > 0.5:
                print(f"Event detected: {result.get('name')}", flush=True)
                return result

            print(f"Not an event or low confidence", flush=True)
            return None
        except Exception as e:
            print(f"Error in LLM check: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return None

    def parse_event_message(self, content: str) -> dict | None:
        """
        Parse a message for event scheduling using LLM only.

        Returns:
            dict with event details, or None if not an event scheduling message
        """
        # Use LLM to determine if this is an event scheduling message
        result = self.llm_check(content)

        if result:
            # Ensure name is always set for valid events
            if not result.get('name'):
                result['name'] = self._generate_event_name(content)

            # Convert datetime_hint to ISO format
            datetime_hint = result.get('datetime_hint')
            if datetime_hint:
                iso_datetime = self._convert_to_iso_datetime(datetime_hint)
                if iso_datetime:
                    result['event_date'] = iso_datetime
                else:
                    result['event_date'] = None
            else:
                result['event_date'] = None

        return result

    def _generate_event_name(self, content: str) -> str:
        """
        Generate a descriptive event name from the message content using Claude.
        """
        try:
            response = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Generate a short, catchy event/activity name (2-4 words) based on this message: "{content}"

Examples:
- "wanna get coffee" -> "Coffee Meetup"
- "go to mcdonalds" -> "McDonald's Hangout"
- "movie night this friday" -> "Movie Night"

Respond with ONLY the event name, nothing else."""
                    }
                ]
            )

            name = response.content[0].text.strip()
            print(f"Generated event name: {name}", flush=True)
            return name if name else "Social Event"
        except Exception as e:
            print(f"Error generating event name: {e}", flush=True)
            return "Social Event"

    def _convert_to_iso_datetime(self, datetime_hint: str) -> str | None:
        """
        Convert a natural language datetime hint to ISO format using Claude.
        Falls back to simple heuristics if LLM fails.
        """
        try:
            response = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Convert this date/time mention to ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
Today's date is {datetime.now().strftime('%Y-%m-%d')}.

Date/time mention: "{datetime_hint}"

Respond with ONLY the ISO datetime, nothing else. If you cannot determine a valid datetime, respond with "INVALID"."""
                    }
                ]
            )

            iso_str = response.content[0].text.strip()

            if iso_str == "INVALID" or not iso_str:
                return None

            # Validate it's actually ISO format
            datetime.fromisoformat(iso_str)
            return iso_str
        except Exception as e:
            print(f"Error converting datetime: {e}")
            return None

    def check_event_similarity(self, new_event: dict) -> bool:
        """
        Check if the new event is semantically similar to any recently scheduled events.
        Uses Claude's conversation history as the source of truth for recently scheduled events.
        Returns True if a duplicate is found, False otherwise.
        """
        try:
            # Add question to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": f"""I'm about to schedule a new event. Based on our conversation history and events we've already scheduled,
is this new event a duplicate or the same event as something we already scheduled?

New event details:
- Name: {new_event.get('name', 'Unknown')}
- Location: {new_event.get('location', 'TBD')}
- When: {new_event.get('datetime_hint', 'TBD')}
- Description: {new_event.get('description', 'None')}

Look through our recent conversation and event scheduling history. Is this the same event we already scheduled,
or is it a different event?

Respond with only "YES" if it's a duplicate (same event), "NO" if it's different."""
            })

            response = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=100,
                messages=self.conversation_history
            )

            response_text = response.content[0].text.strip().upper()

            # Add Claude's response to history for continuity
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })

            # Keep conversation history manageable (last 20 exchanges)
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]

            print(f"Similarity check response: {response_text}", flush=True)

            return "YES" in response_text

        except Exception as e:
            print(f"Error checking event similarity: {e}", flush=True)
            return False

    def add_to_agent_context(self, event_details: dict) -> None:
        """
        Add a scheduled event to Claude's conversation history as context.
        This becomes part of the agent's memory for deduplication.
        """
        try:
            event_summary = f"""Event scheduled:
- Name: {event_details.get('name', 'Unknown')}
- Location: {event_details.get('location', 'TBD')}
- When: {event_details.get('datetime_hint', 'TBD')}
- Description: {event_details.get('description', 'None')}

This event has been scheduled and saved. Remember this for future duplicate detection."""

            self.conversation_history.append({
                "role": "assistant",
                "content": event_summary
            })

            # Keep conversation history manageable
            if len(self.conversation_history) > 40:
                self.conversation_history = self.conversation_history[-40:]

            print(f"Added to agent context: {event_details.get('name')}", flush=True)

        except Exception as e:
            print(f"Error adding to agent context: {e}", flush=True)

    def extract_event_info_from_thread(self, message_content: str, missing_fields: list) -> dict | None:
        """
        Extract missing event information from a thread response.
        Returns a dict with the extracted fields.
        """
        try:
            missing_str = ", ".join(missing_fields)

            response = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Extract the missing event information from this message.
The missing fields are: {missing_str}

Message: "{message_content}"

Respond with a JSON object containing only the fields that are mentioned:
- "name": string (event name/title if mentioned, or null)
- "datetime_hint": string (date/time if mentioned, or null)
- "location": string (location if mentioned, or null)
- "description": string (additional details if mentioned, or null)

Only include fields that are actually present in the message. Return null for missing fields.
Only return valid JSON, no other text."""
                    }
                ]
            )

            response_text = response.content[0].text.strip()

            # Strip markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split('\n', 1)[1] if '\n' in response_text else response_text
                if response_text.endswith("```"):
                    response_text = response_text[:-3].rstrip()

            result = json.loads(response_text)

            # Filter out None values
            filtered_result = {k: v for k, v in result.items() if v is not None}

            print(f"Extracted info from thread: {filtered_result}", flush=True)
            return filtered_result if filtered_result else None

        except Exception as e:
            print(f"Error extracting thread info: {e}", flush=True)
            return None

    def learn_scheduling_pattern(self, message_content: str) -> None:
        """
        Learn from a scheduling message that was previously missed.
        This adds it to the conversation history so Claude can reference it.
        """
        # Add this message to conversation history as a positive example
        learning_prompt = f"""This message should be recognized as a scheduling/event planning message:
"{message_content}"

Remember this pattern and recognize similar messages as event scheduling in the future."""

        self.conversation_history.append({
            "role": "user",
            "content": learning_prompt
        })

        # Add a confirmation to history
        self.conversation_history.append({
            "role": "assistant",
            "content": f"Understood. I've learned that '{message_content[:60]}...' is a scheduling pattern and will recognize similar messages in the future."
        })

        # Store example for reference
        self.scheduling_examples.append(message_content)

        # Keep conversation history manageable (last 20 exchanges)
        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]

        print(f"Learned scheduling pattern: {message_content[:50]}...", flush=True)
        print(f"Total scheduling examples learned: {len(self.scheduling_examples)}", flush=True)

