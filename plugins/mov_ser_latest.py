from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import get_movie_list, get_series_grouped

@Client.on_message(filters.private & filters.command("movies"))
async def list_movies(bot: Client, message: Message):
    movies = await get_movie_list()
    if not movies:
        return await message.reply("❌ No recent movies found.")
    
    msg = "<b>🎬 Latest Movies:</b>\n\n"
    msg += "\n".join(f"✅ <code>{m}</code>" for m in movies)
    await message.reply(msg[:4096], parse_mode=ParseMode.HTML)

@Client.on_message(filters.private & filters.command("series"))
async def list_series(bot: Client, message: Message):
    series_data = await get_series_grouped()
    if not series_data:
        return await message.reply("❌ No recent series episodes found.")
    
    msg = "<b>📺 Latest Series:</b>\n\n"
    for title, episodes in series_data.items():
        ep_list = ", ".join(str(e) for e in episodes)
        msg += f"✅ <b>{title}</b> - Episodes {ep_list}\n"

    await message.reply(msg[:4096], parse_mode=ParseMode.HTML)
