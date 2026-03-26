import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv

# 1. Load the secrets from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_URL = os.getenv('API_URL')

# 2. Setup Intents
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    payload = {
        "user": str(message.author),
        "user_id": message.author.id, # Useful for tracking specific users
        "content": message.content,
        "channel": str(message.channel),
        "timestamp": str(message.created_at) # Good for data records
    }

    try:
        # Use the variable from the .env file
        response = requests.post(TARGET_URL, json=payload, timeout=5)
        print(f"Sent to API: {response.status_code}")
    except Exception as e:
        print(f"Failed to send to API: {e}")

    await bot.process_commands(message)

# 3. Run the bot using the secret token
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: No DISCORD_TOKEN found in environment variables!")