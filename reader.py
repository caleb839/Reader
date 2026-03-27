import discord
import os
from discord.ext import commands

# 1. Configuration - Railway will provide these as strings
TOKEN = os.getenv('DISCORD_TOKEN')
WRITE_ID = int(os.getenv('WRITE_CHANNEL_ID', 0))

# 2. Logic to handle multiple Read IDs from a single string
# Railway Variable Example: READ_CHANNEL_IDS = 123456,789101,112131
raw_read_ids = os.getenv('READ_CHANNEL_IDS', '')
READ_IDS = [int(i.strip()) for i in raw_read_ids.split(',') if i.strip()]

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Listening to {len(READ_IDS)} channels.')

@bot.event
async def on_message(message):
    # Ignore bots and only process if the channel is in our list
    if message.author.bot or message.channel.id not in READ_IDS:
        return

    # Attempt to find the write channel
    write_channel = bot.get_channel(WRITE_ID)
    
    # If not in cache, try to fetch it
    if not write_channel:
        try:
            write_channel = await bot.fetch_channel(WRITE_ID)
        except Exception as e:
            print(f"Error finding write channel: {e}")
            return

    # Send the message
    if write_channel:
        # I added the source channel name so you know where it came from
        await write_channel.send(f"**{message.author}** in #{message.channel.name} said: {message.content}")

    await bot.process_commands(message)

bot.run(TOKEN)
