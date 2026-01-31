import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import datetime
import requests
from event_parser import EventParser

# 1. Setup Intents (Permission to read messages)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize event parser
event_parser = EventParser()

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

# Store incomplete events for threads
incomplete_events = {}  # {thread_id: event_details}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    # Don't process the bot's own messages
    if message.author == bot.user:
        return

    # Format the log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message.guild} | #{message.channel} | {message.author}: {message.content}\n"

    # Save to a text file
    with open("text_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Check if we're in a thread with incomplete event info
    if isinstance(message.channel, discord.Thread):
        if message.channel.id in incomplete_events:
            await process_thread_response(message, incomplete_events[message.channel.id])
            return

    # Check if message is about scheduling an event
    try:
        event_details = event_parser.parse_event_message(message.content)

        if event_details:
            # Check if this is a duplicate of a recent event
            is_duplicate = await check_duplicate_event(message, event_details)
            if not is_duplicate:
                await handle_event_scheduling(message, event_details)
    except Exception as e:
        print(f"Error processing event message: {e}")

    # Still allow commands to work if you add them later
    await bot.process_commands(message)

async def check_duplicate_event(message: discord.Message, event_details: dict) -> bool:
    """
    Check if this event is a duplicate of a recently scheduled event.
    Uses Claude's agent context/conversation history to determine this.
    Returns True if it's a duplicate (should skip scheduling), False otherwise.
    """
    try:
        # Use Claude with its conversation history to check for duplicates
        is_duplicate = event_parser.check_event_similarity(event_details)

        if is_duplicate:
            await message.channel.send(
                "ℹ️ This event seems similar to one we already scheduled recently. "
                "If it's the same event, no need to schedule again! "
                "Reply with `!force` if you want to schedule it anyway."
            )
            return True

        return False

    except Exception as e:
        print(f"Error checking duplicate: {e}")
        return False

async def process_thread_response(message: discord.Message, incomplete_event: dict):
    """
    Process a response in a thread where we're collecting missing event info.
    Use Claude to extract the missing information from the user's response.
    """
    try:
        event_details = incomplete_event['event_details']
        missing_fields = incomplete_event['missing_fields']

        print(f"Processing thread response: {message.content[:50]}...", flush=True)

        # Use Claude to extract the missing information
        extracted_info = event_parser.extract_event_info_from_thread(
            message.content,
            missing_fields
        )

        if extracted_info:
            # Update the event details with extracted info
            event_details.update(extracted_info)

            # Check if we now have all required info
            current_missing = []
            if not event_details.get('name'):
                current_missing.append('name')
            if not event_details.get('datetime_hint'):
                current_missing.append('when')
            if not event_details.get('location'):
                current_missing.append('location')

            if not current_missing:
                # All info is now complete - create the event!
                class MockMessage:
                    def __init__(self, original_msg):
                        self.author = original_msg.author
                        self.content = original_msg.content
                        self.channel = original_msg.channel

                mock_msg = MockMessage(incomplete_event['original_message'])
                await handle_event_scheduling(mock_msg, event_details)

                await message.channel.send("✅ Got it! Event created with all the info you provided!")

                # Clean up
                del incomplete_events[message.channel.id]
            else:
                # Still missing some info
                still_missing = ", ".join(current_missing)
                await message.channel.send(f"⚠️ Thanks! I still need: **{still_missing}**")
        else:
            await message.channel.send("❓ I couldn't extract event info from that message. Could you be more specific?")

    except Exception as e:
        print(f"Error processing thread response: {e}", flush=True)
        await message.channel.send(f"❌ Error: {str(e)}")

async def handle_event_scheduling(message: discord.Message, event_details: dict):
    """Handle event scheduling when a message is detected."""
    try:
        # Check for missing information
        missing_fields = []
        if not event_details.get('name'):
            missing_fields.append('name')
        if not event_details.get('datetime_hint'):
            missing_fields.append('when')
        if not event_details.get('location'):
            missing_fields.append('location')

        # If missing critical info, ask for it
        if missing_fields:
            await ask_for_missing_info(message, event_details, missing_fields)
            return

        # Create event in backend
        event_data = {
            'name': event_details.get('name', 'New Event'),
            'description': event_details.get('description', ''),
            'location': event_details.get('location', ''),
            'event_date': event_details.get('event_date', ''),
            'created_by': message.author.id,
            'created_by_username': message.author.name,
            'status': 'planned'
        }

        response = requests.post(f'{BACKEND_URL}/api/socials', json=event_data)

        if response.status_code == 201:
            event_response = response.json()
            event_id = event_response.get('id')

            # Create scheduling invite link
            invite_link = f"http://localhost:3000/verify?social_id={event_id}"

            # Send message to Discord
            embed = discord.Embed(
                title="📅 Event Scheduled!",
                description=f"**{event_details.get('name', 'New Event')}**",
                color=discord.Color.from_rgb(143, 180, 212)
            )
            embed.add_field(name="Description", value=event_details.get('description', 'No description'), inline=False)
            embed.add_field(name="Location", value=event_details.get('location', 'TBD'), inline=False)
            embed.add_field(name="When", value=event_details.get('datetime_hint', 'TBD'), inline=False)
            embed.add_field(name="RSVP", value=f"[Click here to schedule your availability]({invite_link})", inline=False)
            embed.set_footer(text=f"Created by {message.author.name}")

            await message.channel.send(embed=embed)
            print(f"Event created: {event_details.get('name')} (ID: {event_id})")

            # Add to agent context - tell Claude about this scheduled event for deduplication
            event_parser.add_to_agent_context(event_details)
        else:
            await message.channel.send(f"❌ Error creating event: {response.status_code}")
            print(f"Error creating event: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error handling event scheduling: {e}")
        await message.channel.send(f"❌ Error processing event: {str(e)}")

async def ask_for_missing_info(message: discord.Message, event_details: dict, missing_fields: list):
    """Create a thread to ask for missing event information."""
    try:
        # Create thread for collecting info
        thread = await message.create_thread(
            name=f"📋 Event Details for {event_details.get('name', 'Event')}",
            auto_archive_duration=60
        )

        missing_str = ", ".join(missing_fields)
        embed = discord.Embed(
            title="⚠️ Missing Event Information",
            description=f"I detected an event, but I'm missing some info. Please provide:\n**{missing_str}**",
            color=discord.Color.from_rgb(255, 165, 0)
        )

        if event_details.get('name'):
            embed.add_field(name="Event Name", value=event_details.get('name'), inline=False)
        if event_details.get('description'):
            embed.add_field(name="Description", value=event_details.get('description'), inline=False)
        if event_details.get('datetime_hint'):
            embed.add_field(name="When", value=event_details.get('datetime_hint'), inline=False)
        if event_details.get('location'):
            embed.add_field(name="Location", value=event_details.get('location'), inline=False)

        embed.set_footer(text="Reply in this thread with the missing information")

        await thread.send(embed=embed)
        await message.channel.send(f"✋ I need more info! Check the thread: {thread.mention}")

        # Store the incomplete event data for later completion
        incomplete_events[thread.id] = {
            'original_author': message.author,
            'original_message': message,
            'event_details': event_details,
            'missing_fields': missing_fields
        }
        print(f"Created thread {thread.id} for incomplete event", flush=True)

    except Exception as e:
        print(f"Error creating info thread: {e}")
        await message.channel.send("❌ Could you provide: " + ", ".join(missing_fields))

@bot.command(name='schedule')
async def teach_schedule(ctx):
    """
    Corrects the bot by telling it the previous message was about scheduling.
    Usage: Reply to a message with !schedule to teach the bot it's a scheduling message.
    """
    # Get the message being replied to
    if ctx.message.reference is None:
        await ctx.send("❌ Please reply to a message with `!schedule` to teach me it's a scheduling message.")
        return

    try:
        replied_to = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        message_content = replied_to.content

        # Learn from this correction - add it to conversation history as a scheduling message
        event_parser.learn_scheduling_pattern(message_content)

        # Automatically process it as an event
        event_details = event_parser.parse_event_message(message_content)

        if event_details:
            # Create a mock message object for handle_event_scheduling
            class MockMessage:
                def __init__(self, original_msg):
                    self.author = original_msg.author
                    self.content = original_msg.content
                    self.channel = original_msg.channel

            mock_msg = MockMessage(replied_to)
            await handle_event_scheduling(mock_msg, event_details)
            await ctx.send(f"✅ Learned! I'll remember that messages like \"{message_content[:50]}...\" are about scheduling.")
        else:
            await ctx.send("⚠️ I tried to process it, but couldn't extract event details. Check the message format.")

    except Exception as e:
        print(f"Error in teach_schedule: {e}")
        await ctx.send(f"❌ Error: {str(e)}")

# 2. Start the bot
# Load the variables from .env into the system environment
load_dotenv()

# Retrieve the token
TOKEN = os.getenv('DISCORD_KEY')

bot.run(TOKEN)
