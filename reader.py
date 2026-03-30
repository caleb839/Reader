import discord
import os
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
WRITE_ID = int(os.getenv('WRITE_CHANNEL_ID', 0))
raw_read_ids = os.getenv('READ_CHANNEL_IDS', '')
READ_IDS = [int(i.strip()) for i in raw_read_ids.split(',') if i.strip()]

intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- Bot Status: Online ---')
    print(f'Logged in as: {bot.user}')
    
    # Check Read Channels
    print(f'Checking Read Channels...')
    found_any = False
    for r_id in READ_IDS:
        channel = bot.get_channel(r_id)
        if channel:
            print(f'✅ Listening to: #{channel.name} (ID: {r_id}) in Server: {channel.guild.name}')
            found_any = True
        else:
            print(f'❌ ERROR: Could not find channel ID {r_id}. Is the bot in that server?')
    
    if not found_any:
        print("⚠️ WARNING: The bot is not successfully listening to ANY channels. Check your IDs.")

@bot.event
async def on_message(message):
    # Log to terminal when any message is seen in a watched channel
    if message.channel.id in READ_IDS and not message.author.bot:
        print(f"📩 New message detected from {message.author} in #{message.channel.name}")

    if message.author.bot or message.channel.id not in READ_IDS:
        return

    write_channel = bot.get_channel(WRITE_ID)
    if not write_channel:
        try:
            write_channel = await bot.fetch_channel(WRITE_ID)
        except:
            print(f"❌ Could not find Write Channel ID: {WRITE_ID}")
            return

    # --- 1. HANDLE REPLIES ---
    reply_info = ""
    if message.reference and message.reference.resolved:
        ref = message.reference.resolved
        if isinstance(ref, discord.Message):
            content_snippet = (ref.content[:50] + '...') if len(ref.content) > 50 else ref.content
            reply_info = f"*(Replying to {ref.author}: {content_snippet})*\n"

    # --- 2. HANDLE EMBEDS ---
    embed_text = ""
    if message.embeds:
        for embed in message.embeds:
            if embed.description:
                embed_text += f"\n[Embed Content]: {embed.description}"
            if embed.title:
                embed_text += f"\n[Embed Title]: {embed.title}"

    # --- 3. CONSTRUCT THE TEXT ---
    final_content = (
        f"{reply_info}"
        f"**Trader:** {message.author}\n"
        f"**Message:** {message.content if message.content else '(No text content)'}"
        f"{embed_text}"
    )

    # --- 4. HANDLE IMAGES/FILES ---
    files = []
    if message.attachments:
        for attachment in message.attachments:
            files.append(await attachment.to_file())

    # --- 5. SEND EVERYTHING ---
    try:
        await write_channel.send(content=final_content, files=files)
        print(f"✅ Successfully forwarded message to {write_channel.name}")
    except Exception as e:
        print(f"❌ Failed to forward message: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
