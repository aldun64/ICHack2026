import re
import os
import json
from openai import OpenAI
from datetime import datetime, timedelta

class EventParser:
    """Parse Discord messages for event scheduling using heuristics and LLM."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Heuristic patterns to detect potential event scheduling messages
    SCHEDULING_KEYWORDS = [
        'schedule', 'plan', 'event', 'meetup', 'hangout', 'party', 'gathering',
        'social', 'get together', 'meet up', 'coffee', 'lunch', 'dinner', 'drinks',
        'brunch', 'night out', 'game night', 'watch party', 'movie', 'concert'
    ]

    TIME_KEYWORDS = [
        'today', 'tomorrow', 'tonight', 'this week', 'next week', 'next month',
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
        'september', 'october', 'november', 'december', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'am', 'pm',
        'at', 'on', 'at', 'o\'clock', 'noon', 'midnight'
    ]

    LOCATION_KEYWORDS = [
        'at', 'place', 'location', 'venue', 'cafe', 'restaurant', 'bar', 'park',
        'house', 'home', 'my place', 'your place', 'downtown', 'uptown', 'near'
    ]

    @staticmethod
    def _heuristic_check(content: str) -> bool:
        """
        Quick heuristic check to see if message might be about scheduling an event.
        Returns True if the message contains multiple indicators of event scheduling.
        """
        content_lower = content.lower()

        # Count keyword matches
        scheduling_matches = sum(1 for keyword in EventParser.SCHEDULING_KEYWORDS if keyword in content_lower)
        time_matches = sum(1 for keyword in EventParser.TIME_KEYWORDS if keyword in content_lower)
        location_matches = sum(1 for keyword in EventParser.LOCATION_KEYWORDS if keyword in content_lower)

        # Need at least one scheduling keyword + one time/location indicator
        # This reduces false positives
        has_scheduling = scheduling_matches > 0
        has_time_or_location = (time_matches > 0 or location_matches > 0)

        return has_scheduling and has_time_or_location

    def llm_check(self, content: str) -> dict | None:
        """
        Use OpenAI to determine if this is an event scheduling message
        and extract the event details if it is.

        Returns:
            dict with keys: name, location, description, datetime_hint, is_event
            None if LLM decides it's not an event scheduling message
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Analyze this Discord message to determine if it's someone scheduling/planning a social event or gathering.

Message: "{content}"

Respond with a JSON object containing:
- "is_event": boolean (true if this is about scheduling/planning a social event)
- "name": string (name/title of the event, or null)
- "location": string (location mentioned, or null)
- "description": string (brief description of what the event is, or null)
- "datetime_hint": string (any date/time mentioned, or null)
- "confidence": number (0-1, confidence this is an event scheduling message)

Only return valid JSON, no other text."""
                    }
                ]
            )

            response_text = response.choices[0].message.content.strip()

            # Parse JSON response
            result = json.loads(response_text)

            # Only return if confidence is reasonable and it's actually an event
            if result.get('is_event') and result.get('confidence', 0) > 0.6:
                return result

            return None
        except Exception as e:
            print(f"Error in LLM check: {e}")
            return None

    def parse_event_message(self, content: str) -> dict | None:
        """
        Parse a message for event scheduling.
        First does a quick heuristic check, then uses LLM for confirmation.

        Returns:
            dict with event details, or None if not an event scheduling message
        """
        # Quick heuristic check first (faster, reduces LLM calls)
        if not self._heuristic_check(content):
            return None

        # If heuristic passes, use LLM to confirm and extract details
        result = self.llm_check(content)

        if result:
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

    def _convert_to_iso_datetime(self, datetime_hint: str) -> str | None:
        """
        Convert a natural language datetime hint to ISO format using LLM.
        Falls back to simple heuristics if LLM fails.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
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

            iso_str = response.choices[0].message.content.strip()

            if iso_str == "INVALID" or not iso_str:
                return None

            # Validate it's actually ISO format
            datetime.fromisoformat(iso_str)
            return iso_str
        except Exception as e:
            print(f"Error converting datetime: {e}")
            return None

    @staticmethod
    def is_potential_event_message(content: str) -> bool:
        """Quick check without LLM - just heuristics."""
        return EventParser._heuristic_check(content)
