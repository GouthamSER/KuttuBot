import asyncio
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import get_movie_list, get_series_grouped


# ✅ FIX: Helper background task for auto-delete (avoids blocking handler)
async def auto_delete(delay, *messages):
    await asyncio.sleep(delay)
    for msg in messages:
        try:
            await msg.delete()
        except Exception:
            pass


@Client.on_message(filters.private & filters.command("movies"))
async def list_movies(bot: Client, message: Message):
    movies = await get_movie_list()
    if not movies:
        msg = await message.reply("❌ No recent movies found.")
        # ✅ FIX: Use background task so handler doesn't block
        asyncio.create_task(auto_delete(5, msg))
        return

    text = "<b>🎬 Latest Movies:</b>\n\n" + "\n".join(f"✅ <code>{m}</code>" for m in movies)
    msg = await message.reply(text[:4096], parse_mode=ParseMode.HTML)

    # ✅ FIX: Auto-delete runs in background — handler returns immediately
    asyncio.create_task(auto_delete(120, msg, message))


@Client.on_message(filters.private & filters.command("series"))
async def list_series(bot: Client, message: Message):
    series_data = await get_series_grouped()
    if not series_data:
        msg = await message.reply("❌ No recent series episodes found.")
        # ✅ FIX: Background delete
        asyncio.create_task(auto_delete(5, msg))
        return

    text = "<b>📺 Latest Series:</b>\n\n"
    for title, episodes in series_data.items():
        ep_list = ", ".join(str(e) for e in episodes)
        text += f"✅ <b>{title}</b> - Episodes {ep_list}\n"

    msg = await message.reply(text[:4096], parse_mode=ParseMode.HTML)

    # ✅ FIX: Auto-delete runs in background — handler returns immediately
    asyncio.create_task(auto_delete(120, msg, message))
