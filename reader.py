import discord
import os
import sys
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
WRITE_ID_RAW = os.getenv('WRITE_CHANNEL_ID', '0')
WRITE_ID = int(WRITE_ID_RAW) if WRITE_ID_RAW.isdigit() else 0

raw_read_ids = os.getenv('READ_CHANNEL_IDS', '')
READ_IDS = [int(i.strip()) for i in raw_read_ids.split(',') if i.strip()]

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'\n--- 🤖 BOT STARTUP ---')
    print(f'Logged in as: {bot.user}')
    
    # 1. Check Write Channel (Destination)
    print(f'\n--- 📝 CHECKING WRITE CHANNEL ---')
    try:
        write_channel = bot.get_channel(WRITE_ID) or await bot.fetch_channel(WRITE_ID)
        print(f'✅ DESTINATION FOUND: #{write_channel.name} in Server: {write_channel.guild.name}')
    except Exception as e:
        print(f'❌ ERROR: Could not find Write Channel ID {WRITE_ID}.')
        print(f'   Reason: {e}')
        print(f'   Check if the bot is invited to the destination server.')

    # 2. Check Read Channels (Sources)
    print(f'\n--- 📢 CHECKING READ CHANNELS ---')
    found_any = False
    if not READ_IDS:
        print("⚠️ WARNING: READ_CHANNEL_IDS is empty in your Railway variables!")
    
    for r_id in READ_IDS:
        try:
            channel = bot.get_channel(r_id) or await bot.fetch_channel(r_id)
            print(f'✅ LISTENING TO: #{channel.name} (ID: {r_id}) in Server: {channel.guild.name}')
            found_any = True
        except Exception as e:
            print(f'❌ ERROR: Access denied to Read Channel {r_id}.')
            print(f'   Reason: {e}')
    
    print(f'\n--- 🚀 BOT IS FULLY OPERATIONAL ---\n')

@bot.event
async def on_message(message):
    # Log everything to Railway console to see if it's "hearing" messages
    if message.channel.id in READ_IDS and not message.author.bot:
        print(f"📩 Heard message from {message.author} in #{message.channel.name}: {message.content[:30]}...")

    # Filter
    if message.author.bot or message.channel.id not in READ_IDS:
        return

    # Find Write Channel
    write_channel = bot.get_channel(WRITE_ID)
    if not write_channel:
        try:
            write_channel = await bot.fetch_channel(WRITE_ID)
        except:
            return

    # Handle Replies
    reply_info = ""
    if message.reference and message.reference.resolved:
        ref = message.reference.resolved
        if isinstance(ref, discord.Message):
            content_snippet = (ref.content[:50] + '...') if len(ref.content) > 50 else ref.content
            reply_info = f"*(Replying to {ref.author}: {content_snippet})*\n"

    # Handle Embeds
    embed_text = ""
    if message.embeds:
        for embed in message.embeds:
            if embed.description: embed_text += f"\n[Embed]: {embed.description}"
            elif embed.title: embed_text += f"\n[Embed]: {embed.title}"

    # Construct Content
    final_content = (
        f"{reply_info}"
        f"**Trader:** {message.author}\n"
        f"**Message:** {message.content if message.content else '(No text)'}"
        f"{embed_text}"
    )

    # Handle Attachments
    files = []
    if message.attachments:
        for attachment in message.attachments:
            files.append(await attachment.to_file())

    # Send
    try:
        await write_channel.send(content=final_content, files=files)
        print(f"✅ Forwarded successfully.")
    except Exception as e:
        print(f"❌ Failed to forward: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
