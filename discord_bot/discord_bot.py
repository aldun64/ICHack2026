import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import datetime


# 1. Setup Intents (Permission to read messages)
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_message(message):
    # Don't log the bot's own messages
    if message.author == bot.user:
        return

    # Format the log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message.guild} | #{message.channel} | {message.author}: {message.content}\n"

    # Save to a text file
    with open("text_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Still allow commands to work if you add them later
    await bot.process_commands(message)

# 2. Start the bot
# Load the variables from .env into the system environment
load_dotenv()

# Retrieve the token
TOKEN = os.getenv('DISCORD_KEY')

bot.run(TOKEN)
