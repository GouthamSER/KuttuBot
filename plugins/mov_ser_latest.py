import asyncio
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.types import Message
from database.ia_filterdb import get_movie_list, get_series_grouped

@Client.on_message(filters.private & filters.command("movies"))
async def list_movies(bot: Client, message: Message):
    movies = await get_movie_list()
    if not movies:
        msg = await message.reply("❌ No recent movies found.")
        await msg.delete()
        return
    
    text = "<b>🎬 Latest Movies:</b>\n\n" + "\n".join(f"✅ <code>{m}</code>" for m in movies)
    msg = await message.reply(text[:4096], parse_mode=ParseMode.HTML)
    
    # Auto-delete after 2 minutes
    await asyncio.sleep(120)
    await msg.delete()
    await message.delete()  # optional: delete user command

@Client.on_message(filters.private & filters.command("series"))
async def list_series(bot: Client, message: Message):
    series_data = await get_series_grouped()
    if not series_data:
        msg = await message.reply("❌ No recent series episodes found.")
        await msg.delete()
        return
    
    text = "<b>📺 Latest Series:</b>\n\n"
    for title, episodes in series_data.items():
        ep_list = ", ".join(str(e) for e in episodes)
        text += f"✅ <b>{title}</b> - Episodes {ep_list}\n"

    msg = await message.reply(text[:4096], parse_mode=ParseMode.HTML)
    
    # Auto-delete after 2 minutes
    await asyncio.sleep(120)
    await msg.delete()
    await message.delete()  # optional: delete user command
