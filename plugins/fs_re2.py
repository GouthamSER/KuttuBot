#  @MrMNTG @MusammilN  ADDED TO THIS BOT @GouthamSER
from pyrogram import filters, Client
from pyrogram.types import Message
from utils import JOIN_REQUEST_USERS
from info import ADMINS

@Client.on_message(filters.command("clear_join_users") & filters.user(ADMINS))
async def clear_join_users(_, message: Message):
    JOIN_REQUEST_USERS.clear()
    await message.reply_text("✅ Cleared all join request users.")
