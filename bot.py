import logging
import logging.config
import pytz
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media, Media2, choose_mediaDB, db as clientDB
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, SECONDDB_URI
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
from datetime import date, datetime
from sample_info import tempDict

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        # Fetch banned users and chats
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        
        # Start bot
        await super().start()
        
        # Ensure media indexes are created
        await Media.ensure_indexes()
        await Media2.ensure_indexes()

        # Choose the correct DB based on available space
        stats = await clientDB.command('dbStats')
        free_dbSize = round(512 - ((stats['dataSize'] / (1024 * 1024)) + (stats['indexSize'] / (1024 * 1024))), 2)
        
        if SECONDDB_URI and free_dbSize < 10:  # If primary DB has less than 10MB left, use secondary DB
            tempDict["indexDB"] = SECONDDB_URI
            logging.info(f"Primary DB has only {free_dbSize} MB left, switching to Secondary DB for storing data.")
        elif SECONDDB_URI is None:
            logging.error("SECONDDB_URI is missing! Exiting...")
            exit()
        else:
            logging.info(f"Primary DB has enough space ({free_dbSize}MB left), using primary DB for data storage.")
        
        await choose_mediaDB()

        # Get bot info and set up
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        
        logging.info(f"{me.first_name} for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        logging.info(script.LOGO)

        # Sending a restart message to log channel
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially."""
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

app = Bot()
app.run()
