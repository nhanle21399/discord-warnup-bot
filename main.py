import discord
from discord.ext import commands, tasks
import datetime
from datetime import timezone, timedelta

# ==========================
# Config
# ==========================
GUILD_ID = 1249195207199555686
IMAGE_CHANNEL_ID = 1376858868503810088
REPORT_CHANNEL_ID = 1399403753387593789
USER_IDS = [
    784686080887750686, 624112042164617217, 851172665015140384,
    438929813881880597, 465024426975690752, 1145230290357325904,
    1339909532855308380, 1238521887483625474
]

# ==========================
# Init
# ==========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
VN_TZ = timezone(timedelta(hours=7))


@client.event
async def on_ready():
    print(f"Đã đăng nhập dưới tên {client.user}")
    check_warnup_loop.start()


# ==========================
# Check Warnup Function
# ==========================
async def perform_warnup_check():
    guild = client.get_guild(GUILD_ID)
    image_channel = guild.get_channel(IMAGE_CHANNEL_ID)
    report_channel = guild.get_channel(REPORT_CHANNEL_ID)

    today = datetime.datetime.utcnow().astimezone(VN_TZ).date()
    messages = [msg async for msg in image_channel.history(limit=200)]

    submitted_ids = set()
    for msg in messages:
        msg_date = msg.created_at.replace(
            tzinfo=timezone.utc).astimezone(VN_TZ).date()
        if msg_date == today and msg.attachments:
            submitted_ids.add(msg.author.id)

    missing = []
    for user_id in USER_IDS:
        if user_id not in submitted_ids:
            user = guild.get_member(user_id)
            if user:
                missing.append(user.mention)

    if missing:
        await report_channel.send(
            f"**❌ Những người chưa gửi hình warnup ngày {today.strftime('%d/%m/%Y')}:**\n"
            + "\n".join(missing))
    else:
        await report_channel.send(
            f"✅ Tất cả đã gửi hình warnup ngày {today.strftime('%d/%m/%Y')}!")


# ==========================
# Auto Check at 10:00PM VN
# ==========================
@tasks.loop(time=datetime.time(hour=15, minute=0, tzinfo=datetime.timezone.utc))  # 10:00PM VN
async def check_warnup_loop():
    await perform_warnup_check()

# ==========================
# Manual Command: !check
# ==========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_message(message):
    if message.content == "!ping":
        await message.channel.send("pong")

@client.event
async def on_ready():
    print(f"Đã đăng nhập dưới tên {client.user}")
    check_warnup_loop.start()
    

from keep_alive import keep_alive
keep_alive()

import os
TOKEN = os.getenv("TOKEN")

print("TOKEN check:", TOKEN)  # Để debug
