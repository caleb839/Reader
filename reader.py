import discord
import requests
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_URL = os.getenv('API_URL')

# Get both IDs from environment variables
READ_ID = int(os.getenv('READ_CHANNEL_ID', 0))
WRITE_ID = int(os.getenv('WRITE_CHANNEL_ID', 0))

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_message(message):
    # 1. Prevent loops and ignore other channels
    if message.author.bot or message.channel.id != READ_ID:
        return

    # 2. Prepare the data for your API
    payload = {
        "user": str(message.author),
        "content": message.content,
        "from_server": str(message.guild.name)
    }

    # 3. Action A: Send to the API (Webhook)
    try:
        requests.post(TARGET_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"API Error: {e}")

    # 4. Action B: Write to the other server
    write_channel = bot.get_channel(WRITE_ID)
    if write_channel:
        await write_channel.send(f"**{message.author}** said: {message.content}")
    else:
        print("Error: Could not find the Write Channel. Is the bot in that server?")

    await bot.process_commands(message)

bot.run(TOKEN)
