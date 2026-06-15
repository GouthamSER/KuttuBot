#!/usr/bin/env python3
# works taken from wzml-x thanks to me implement here :)
import logging
from os import path as ospath, getcwd
from re import search as re_search
from shlex import split as ssplit

from aiofiles import open as aiopen
from aiofiles.os import mkdir, path as aiopath, remove as aioremove
from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.handlers import MessageHandler

from helper import cmd_exec, telegraph

LOGGER = logging.getLogger(__name__)

# ── section emoji map ────────────────────────────────────────────────────────
_SECTIONS = {"General": "🗒", "Video": "🎞", "Audio": "🔊", "Text": "🔠", "Menu": "🗃"}


def _parse_mediainfo(raw: str) -> str:
    """Convert raw mediainfo stdout → Telegraph-ready HTML."""
    tc = ""
    trigger = False
    for line in raw.split("\n"):
        for section, emoji in _SECTIONS.items():
            if line.startswith(section):
                trigger = True
                if not line.startswith("General"):
                    tc += "</pre><br>"
                tc += f"<h4>{emoji} {line.replace('Text', 'Subtitle')}</h4>"
                break
        if trigger:
            tc += "<br><pre>"
            trigger = False
        else:
            tc += line + "\n"
    tc += "</pre><br>"
    return tc


async def gen_mediainfo(client, message, link=None, media=None, media_msg=None):
    status = await message.reply_text("<i>Generating MediaInfo…</i>")
    des_path = None
    try:
        folder = "Mediainfo/"
        if not await aiopath.isdir(folder):
            await mkdir(folder)

        if link:
            filename = re_search(r".+/(.+)", link)
            filename = filename.group(1) if filename else "file"
            des_path = ospath.join(folder, filename)
            headers = {
                "user-agent": (
                    "Mozilla/5.0 (Linux; Android 12; 2201116PI) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/107.0.0.0 Mobile Safari/537.36"
                )
            }
            async with ClientSession() as session:
                async with session.get(link, headers=headers) as resp:
                    async with aiopen(des_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(10_000_000):
                            await f.write(chunk)
                            break  # first chunk only — enough for mediainfo

        elif media:
            des_path = ospath.join(folder, media.file_name or "media_file")
            if media.file_size <= 50_000_000:
                await media_msg.download(ospath.join(getcwd(), des_path))
            else:
                # stream first ~5 MB so mediainfo can read headers
                async for chunk in client.stream_media(media, limit=5):
                    async with aiopen(des_path, "ab") as f:
                        await f.write(chunk)

        stdout, stderr, rc = await cmd_exec(ssplit(f'mediainfo "{des_path}"'))
        if rc != 0 or not stdout:
            raise RuntimeError(stderr or "mediainfo returned no output")

        title    = f"📌 {ospath.basename(des_path)}"
        content  = f"<h4>{title}</h4><br><br>" + _parse_mediainfo(stdout)
        page     = await telegraph.create_page(title="MediaInfo", content=content)
        graph_url = f"https://graph.org/{page['path']}"
        await status.edit_text(
            f"<b>MediaInfo:</b>\n\n➲ <b>Link:</b> {graph_url}",
            disable_web_page_preview=False,
        )

    except Exception as exc:
        LOGGER.error(exc)
        await status.edit_text(f"<b>Error:</b> {exc}")
    finally:
        if des_path and await aiopath.exists(des_path):
            await aioremove(des_path)


async def mediainfo(client, message):
    rply = message.reply_to_message
    help_text = (
        "<b>Usage:</b>\n"
        "• Reply to a media file: <code>/mi</code>\n"
        "• Pass a direct URL: <code>/mi https://…/file.mkv</code>"
    )

    # link passed inline or reply-to text
    if len(message.command) > 1:
        return await gen_mediainfo(client, message, link=message.command[1])
    if rply and rply.text:
        return await gen_mediainfo(client, message, link=rply.text.strip())

    # reply to media
    if rply:
        media = (
            rply.document
            or rply.video
            or rply.audio
            or rply.voice
            or rply.animation
            or rply.video_note
        )
        if media:
            return await gen_mediainfo(client, message, media=media, media_msg=rply)

    await message.reply_text(help_text)


def register(bot):
    bot.add_handler(
        MessageHandler(mediainfo, filters=filters.command(["mediainfo", "mi"]))
    )
