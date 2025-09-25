import logging
import logging.config
from datetime import datetime, timedelta, date
import os
import sys

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

# for prevent stoping the bot after 1 week
logging.getLogger("asyncio").setLevel(logging.CRITICAL -1)
import tgcrypto
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
import asyncio
import pytz

# peer id invaild fixxx
from pyrogram import utils as pyroutils
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

from plugins.webcode import bot_run
from os import environ
from aiohttp import web as webserver

PORT_CODE = environ.get("PORT", "8080")

async def preload_auth_channels():
    if not await db.get_auth_channels():
        await db.set_auth_channels(DEFAULT_AUTH_CHANNELS)
        logging.info("Set default AUTH_CHANNELs in DB.")

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT)#RESTART SND IN LOG_CHANNEL
        print("Goutham SER own Bot</>")

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_GC_TXT.format(today, time))
        client = webserver.AppRunner(await bot_run())
        await client.setup()
        bind_address = "0.0.0.0"
        await webserver.TCPSite(client, bind_address,
        PORT_CODE).start()
        
        # Schedule auto-restart every 24 hours
        asyncio.create_task(self.schedule_restart())

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    # 24 hrs restart fn()
    async def restart(self):
        logging.info("Restarting bot process...")
        await self.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    async def schedule_restart(self, hours: int = 24):
        await asyncio.sleep(hours * 60 * 60)  # Wait for 24 hours
        await self.send_message(chat_id=LOG_CHANNEL, text="Auto Restarting the KuttuBot \n(24 hrs ⏰️ refresh)...")
        await self.restart()
#restarting fn() end;
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


app = Bot()
app.run()
