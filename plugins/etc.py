import random
import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import Client, filters, enums
from pyrogram.types import *
from info import ADMINS
from utils import humanbytes
from urllib.parse import quote_plus

CMD = ["/", "."]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#              🏓  PING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("<b>⚡ Pinging...</b>", parse_mode=enums.ParseMode.HTML)
    end_t = time.time()
    ms = (end_t - start_t) * 1000

    if ms < 100:
        quality = "🟢 Excellent"
    elif ms < 300:
        quality = "🟡 Good"
    else:
        quality = "🔴 Slow"

    await rm.edit_text(
        f"<b>🏓 Pong!</b>\n\n"
        f"<b>┌ Latency  :</b> <code>{ms:.3f} ms</code>\n"
        f"<b>└ Quality  :</b> {quality}",
        parse_mode=enums.ParseMode.HTML
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#             🔄  RESTART
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart(bot, message):
    msg = await bot.send_message(
        chat_id=message.chat.id,
        text=(
            "<b>🔄 Restarting Bot...</b>\n\n"
            "<blockquote>⏳ Please wait a moment.\n"
            "All systems will be back online shortly.</blockquote>"
        ),
        parse_mode=enums.ParseMode.HTML
    )
    await asyncio.sleep(3)
    await msg.edit_text(
        "<b>✅ Bot Restarted Successfully!</b>\n\n"
        "<blockquote>🚀 All systems are back online.\n"
        "Ready to serve you 💯</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    os.execl(sys.executable, sys.executable, *sys.argv)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          📊  LIVE USAGE MONITOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_START_TIME = time.time()


def make_bar(percentage: float, length: int = 10) -> str:
    """Create a styled progress bar."""
    filled = int(length * percentage / 100)
    empty = length - filled
    return "█" * filled + "░" * empty


def get_status_emoji(percentage: float) -> str:
    """Return colour emoji based on usage level."""
    if percentage < 50:
        return "🟢"
    elif percentage < 80:
        return "🟡"
    return "🔴"


@Client.on_message(filters.command("usage"))
async def live_usage(bot, update):
    msg = await bot.send_message(
        chat_id=update.chat.id,
        text="<b>⚙️ Initializing System Monitor...</b>",
        parse_mode=enums.ParseMode.HTML
    )

    start_time = time.time()

    while True:
        uptime_seconds = int(time.time() - BOT_START_TIME)
        currentTime = format_uptime_short(uptime_seconds)

        total, used, free = shutil.disk_usage(".")
        total_hr  = humanbytes(total)
        used_hr   = humanbytes(used)
        free_hr   = humanbytes(free)

        cpu_pct  = psutil.cpu_percent(interval=0.5)
        ram_pct  = psutil.virtual_memory().percent
        disk_pct = psutil.disk_usage('/').percent

        elapsed = int(time.time() - start_time)
        remaining = max(0, 60 - elapsed)

        text = (
            f"<b>⚙️ 𝖱𝖾𝖺𝗅-𝖳𝗂𝗆𝖾 𝖡𝗈𝗍 𝖲𝗍𝖺𝗍𝗎𝗌</b>  <i>(Koyeb)</i>\n"
            f"{'━' * 28}\n\n"

            f"🕔 <b>Uptime</b>   » <code>{currentTime}</code>\n\n"

            f"🖥 <b>CPU</b>  {get_status_emoji(cpu_pct)}  <code>{cpu_pct:.1f}%</code>\n"
            f"   <code>[{make_bar(cpu_pct)}]</code>\n\n"

            f"🧠 <b>RAM</b>  {get_status_emoji(ram_pct)}  <code>{ram_pct:.1f}%</code>\n"
            f"   <code>[{make_bar(ram_pct)}]</code>\n\n"

            f"💾 <b>Disk</b>  {get_status_emoji(disk_pct)}  <code>{disk_pct:.1f}%</code>\n"
            f"   <code>[{make_bar(disk_pct)}]</code>\n\n"

            f"{'━' * 28}\n"
            f"📦 <b>Total</b>  » <code>{total_hr}</code>\n"
            f"🗳 <b>Used</b>   » <code>{used_hr}</code>\n"
            f"📂 <b>Free</b>   » <code>{free_hr}</code>\n"
            f"{'━' * 28}\n\n"
            f"⏱ <i>Auto-stops in {remaining}s  •  Refreshes every 5s</i>"
        )

        try:
            await msg.edit_text(text, parse_mode=enums.ParseMode.HTML)
        except Exception:
            break

        if time.time() - start_time > 60:
            await msg.edit_text(
                text.replace(
                    f"⏱ <i>Auto-stops in {remaining}s  •  Refreshes every 5s</i>",
                    "✅ <b>Monitoring complete.</b>"
                ),
                parse_mode=enums.ParseMode.HTML
            )
            break

        await asyncio.sleep(5)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           ⏱  UPTIME FORMATTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_uptime_short(seconds: int) -> str:
    YEAR   = 31536000
    MONTH  = 2592000
    WEEK   = 604800
    DAY    = 86400
    HOUR   = 3600
    MINUTE = 60

    years,   rem = divmod(seconds, YEAR)
    months,  rem = divmod(rem,     MONTH)
    weeks,   rem = divmod(rem,     WEEK)
    days,    rem = divmod(rem,     DAY)
    hours,   rem = divmod(rem,     HOUR)
    minutes, sec = divmod(rem,     MINUTE)

    parts = []
    if years:   parts.append(f"{years}y")
    if months:  parts.append(f"{months}mo")
    if weeks:   parts.append(f"{weeks}w")
    if days:    parts.append(f"{days}d")
    if hours:   parts.append(f"{hours}hr")
    if minutes: parts.append(f"{minutes}m")
    if sec or not parts: parts.append(f"{sec}s")

    return " ".join(parts)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#           🔗  LINK GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("link") & filters.user(ADMINS))
async def generate_link(client, message):
    """Generate a shareable Telegram deep link for a movie/file."""
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "<b>❗ No Movie Name Provided!</b>\n\n"
                "<blockquote>"
                "📌 <b>Usage:</b>  <code>/link &lt;movie name&gt;</code>\n\n"
                "📎 <b>Example:</b>\n"
                "   <code>/link game of thrones</code>\n"
                "   <code>/link KGF Chapter 2</code>"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )

        bot_username = client.me.username
        movie_query  = " ".join(message.command[1:]).lower()
        movie_slug   = quote_plus(movie_query.replace(" ", "-"))
        link         = f"https://t.me/{bot_username}?start=getfile-{movie_slug}"
        share_url    = f"https://telegram.me/share/url?url={link}"

        # Clean display name — title case
        display_name = " ".join(message.command[1:]).title()

        await message.reply_text(
            f"<b>🔗 Deep Link Generated!</b>\n\n"
            f"{'━' * 28}\n"
            f"🎬 <b>Movie  :</b>  <code>{display_name}</code>\n"
            f"🤖 <b>Bot    :</b>  @{bot_username}\n"
            f"{'━' * 28}\n\n"
            f"📎 <b>Your Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"<i>👇 Tap the button below to share it instantly!</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📤 Share This Link", url=share_url),
            ]]),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        print(f"[generate_link] Error: {e}")
        await message.reply_text(
            "<b>⚠️ Something went wrong!</b>\n\n"
            "<blockquote>Please try again or contact the admin.</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
