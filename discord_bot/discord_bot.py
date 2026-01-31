import discord
from discord.ext import commands
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

    # Check if message is about scheduling an event
    try:
        event_details = event_parser.parse_event_message(message.content)

        if event_details:
            await handle_event_scheduling(message, event_details)
    except Exception as e:
        print(f"Error processing event message: {e}")

    # Still allow commands to work if you add them later
    await bot.process_commands(message)

async def handle_event_scheduling(message: discord.Message, event_details: dict):
    """Handle event scheduling when a message is detected."""
    try:
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
        else:
            await message.channel.send(f"❌ Error creating event: {response.status_code}")
            print(f"Error creating event: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error handling event scheduling: {e}")
        await message.channel.send(f"❌ Error processing event: {str(e)}")

# 2. Start the bot
# Load the variables from .env into the system environment
load_dotenv()

# Retrieve the token
TOKEN = os.getenv('DISCORD_KEY')

bot.run(TOKEN)
