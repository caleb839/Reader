import discord
import os
import sys
from discord.ext import commands

# --- CONFIGURATION ---
TOKEN = os.getenv('DISCORD_TOKEN')
WRITE_ID_RAW = os.getenv('WRITE_CHANNEL_ID', '0')
WRITE_ID = int(WRITE_ID_RAW) if WRITE_ID_RAW.isdigit() else 0

raw_read_ids = os.getenv('READ_CHANNEL_IDS', '')
READ_IDS = [int(i.strip()) for i in raw_read_ids.split(',') if i.strip()]

# --- BOT SETUP ---
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
        print(f'    Reason: {e}')

    # 2. Check Read Channels (Sources)
    print(f'\n--- 📢 CHECKING READ CHANNELS ---')
    if not READ_IDS:
        print("⚠️ WARNING: READ_CHANNEL_IDS is empty!")
    
    for r_id in READ_IDS:
        try:
            channel = bot.get_channel(r_id) or await bot.fetch_channel(r_id)
            print(f'✅ LISTENING TO: #{channel.name} (ID: {r_id}) in Server: {channel.guild.name}')
        except Exception as e:
            print(f'❌ ERROR: Access denied to Read Channel {r_id}. Reason: {e}')
    
    print(f'\n--- 🚀 BOT IS FULLY OPERATIONAL ---\n')

@bot.event
async def on_message(message):
    # Ignore the bot's own messages to prevent loops
    if message.author.id == bot.user.id:
        return

    # Ensure message is from a monitored channel
    if message.channel.id not in READ_IDS:
        return

    # Find Write Channel
    write_channel = bot.get_channel(WRITE_ID) or await bot.fetch_channel(WRITE_ID)
    if not write_channel:
        return

    # --- HANDLE REPLIES ---
    reply_info = ""
    if message.reference and message.reference.resolved:
        ref = message.reference.resolved
        if isinstance(ref, discord.Message):
            content_snippet = (ref.content[:50] + '...') if len(ref.content) > 50 else ref.content
            reply_info = f"*(Replying to {ref.author}: {content_snippet})*\n"

    # --- HANDLE EMBEDS & IMAGES ---
    # Trading bots like Klopyzx send images (BingX PnL) inside Embed objects.
    embed_text = ""
    image_url = None
    
    if message.embeds:
        for embed in message.embeds:
            if embed.title: 
                embed_text += f"\n**{embed.title}**"
            if embed.description: 
                embed_text += f"\n{embed.description}"
            
            # Check for fields (Entry, TP, SL)
            if embed.fields:
                for field in embed.fields:
                    embed_text += f"\n**{field.name}:** {field.value}"
            
            # CRITICAL FIX: Grab the image URL from the source embed
            if embed.image and embed.image.url:
                image_url = embed.image.url
            elif embed.thumbnail and embed.thumbnail.url:
                image_url = embed.thumbnail.url

    # --- HANDLE ATTACHMENTS (Manual Screenshots) ---
    files = []
    if message.attachments:
        for attachment in message.attachments:
            try:
                files.append(await attachment.to_file())
            except:
                continue

    # --- CONSTRUCT FINAL OUTPUT ---
    msg_body = message.content if message.content else ""
    
    # We create a new Embed to make it look clean and structured
    forward_embed = discord.Embed(
        description=f"{reply_info}**Trader:** {message.author}\n**Message:** {msg_body}\n{embed_text}",
        color=discord.Color.blue()
    )
    
    # If we found a bot image/thumbnail, attach it to our new embed
    if image_url:
        forward_embed.set_image(url=image_url)

    # --- SEND MESSAGE ---
    try:
        # We send the embed (text + bot images) and the files (manual uploads)
        await write_channel.send(embed=forward_embed, files=files)
        print(f"✅ Forwarded message from {message.author} with visual data.")
    except Exception as e:
        print(f"❌ Failed to forward: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
