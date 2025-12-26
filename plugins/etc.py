import random
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import Client, filters, enums
from pyrogram.types import *
from info import ADMINS
from utils import humanbytes



CMD = ["/", "."]

@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...........")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"𝖯𝗂𝗇𝗀!\n{time_taken_s:.3f} ms")

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**𝖡𝗈𝗍 𝖨𝗌 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀...🪄**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**𝖡𝗈𝗍 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ! 𝖱𝖾𝖺𝖽𝗒 𝖳𝗈 𝖬𝗈𝗏𝖾 𝖮𝗇 💯**")
    os.execl(sys.executable, sys.executable, *sys.argv)



BOT_START_TIME = time.time()

def make_bar(percentage: float, length: int = 10) -> str:
    """Create a nice progress bar for usage metrics."""
    filled = int(length * percentage / 100)
    empty = length - filled
    return "▰" * filled + "▱" * empty


@Client.on_message(filters.command("usage"))
async def live_usage(bot, update):
    msg = await bot.send_message(
        chat_id=update.chat.id,
        text="__Initializing system monitor...__",
        parse_mode=enums.ParseMode.MARKDOWN
    )

    start_time = time.time()

    while True:
        uptime_seconds = int(time.time() - BOT_START_TIME)
        currentTime = format_uptime_short(uptime_seconds)

        total, used, free = shutil.disk_usage(".")
        total = humanbytes(total)
        used = humanbytes(used)
        free = humanbytes(free)

        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        cpu_bar = make_bar(cpu_usage)
        ram_bar = make_bar(ram_usage)
        disk_bar = make_bar(disk_usage)

        text = f"""<b>⚙️ 𝖱𝖾𝖺𝗅-𝖳𝗂𝗆𝖾 𝖡𝗈𝗍 𝖲𝗍𝖺𝗍𝗎𝗌 (Koyeb)</b>

🕔 𝖴𝗉𝗍𝗂𝗆𝖾: <code>{currentTime}</code>

🛠 𝖢𝖯𝖴: <code>{cpu_usage:.1f}%</code>
<code>[{cpu_bar}]</code>

🗜 𝖱𝖠𝖬: <code>{ram_usage:.1f}%</code>
<code>[{ram_bar}]</code>

💾 𝖣𝗂𝗌𝗄: <code>{disk_usage:.1f}%</code>
<code>[{disk_bar}]</code>

🗂 𝖳𝗈𝗍𝖺𝗅: <code>{total}</code>
🗳 𝖴𝗌𝖾𝖽: <code>{used}</code>
📝 𝖥𝗋𝖾𝖾: <code>{free}</code>

⏳ Updating live... (refreshes every 5s)
"""

        try:
            await msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception:
            # Ignore if message was deleted or can't be edited
            break

        # Stop after 20 sec to avoid infinite loop (safety)
        if time.time() - start_time > 20:
            await msg.edit_text(
                text + "\n✅ <b>Monitoring stopped (20 sec elapsed)</b>",
                parse_mode=enums.ParseMode.HTML
            )
            break

        await asyncio.sleep(5)



def format_uptime_short(seconds: int) -> str:
    # Define time units in seconds
    YEAR = 31536000      # 365 days
    MONTH = 2592000      # 30 days
    WEEK = 604800        # 7 days
    DAY = 86400
    HOUR = 3600
    MINUTE = 60

    years, rem = divmod(seconds, YEAR)
    months, rem = divmod(rem, MONTH)
    weeks, rem = divmod(rem, WEEK)
    days, rem = divmod(rem, DAY)
    hours, rem = divmod(rem, HOUR)
    minutes, sec = divmod(rem, MINUTE)

    parts = []
    if years > 0:
        parts.append(f"{years}y")
    if months > 0:
        parts.append(f"{months}mo")
    if weeks > 0:
        parts.append(f"{weeks}w")
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}hr")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if sec > 0 or not parts:
        parts.append(f"{sec}s")

    return " ".join(parts)
