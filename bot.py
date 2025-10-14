import logging
import logging.config
from datetime import datetime, timedelta, date
import os
import sys, re

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
from info import RESTART_INTERVAL, SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
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

        try:
            await self.send_message(
                chat_id=LOG_CHANNEL,
                text="✅ Bot Started Successfully!\n⚡ Kuttu Bot¹ 💥"
            )
        except Exception as e:
            logging.error(f"Could not send start message: {e}")
            
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
        asyncio.create_task(self.schedule_restart(RESTART_INTERVAL))

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye 👋")

    async def restart(self):
        logging.info("Restarting bot process...")
        await self.stop()
        # Koyeb/Docker compatible restart
        os._exit(0)

    async def schedule_restart(self, interval: str = RESTART_INTERVAL):
        """
        Automatically restart the bot after the given interval.
        Example interval: '12h', '1d', '30m'
        """
        if not interval:
            logging.warning("No restart interval set — skipping auto-restart.")
            return

        try:
            seconds = parse_interval(interval)
        except Exception as e:
            logging.error(f"Invalid restart interval '{interval}': {e}")
            return

        while True:
            try:
                # Sleep until 1 minute before restart
                await asyncio.sleep(max(0, seconds - 60))
                try:
                    await self.send_message(
                        chat_id=LOG_CHANNEL,
                        text=f"| Kuttu Bot ¹ |\n⚠️ Bot will restart in 1 minute (every {interval}).",
                    )
                except Exception as e:
                    logging.error(f"Could not send restart warning: {e}")

                await asyncio.sleep(60)
                await self.restart()
            except Exception as e:
                logging.error(f"Restart loop error: {e}")
                await asyncio.sleep(60)
    
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


# Helper function: Parse restart interval
def parse_interval(interval: str) -> int:
    """
    Convert interval string like '1h', '2d', '30m' to seconds.
    """
    match = re.match(r"(\d+)([dhm])", interval.lower())
    if not match:
        raise ValueError("Invalid interval format. Use e.g., '1h', '2d', '30m'.")
    value, unit = match.groups()
    value = int(value)
    if unit == "d":
        return value * 24 * 60 * 60
    elif unit == "h":
        return value * 60 * 60
    elif unit == "m":
        return value * 60
    else:
        raise ValueError("Invalid time unit. Only 'd', 'h', 'm' are allowed.")



app = Bot()
app.run()
