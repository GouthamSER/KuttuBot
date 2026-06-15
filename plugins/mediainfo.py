# works taken from wzml-x thanks to me implement here :)
#!/usr/bin/env python3
import asyncio
import logging
import os
from re import search as re_search
from shlex import split as ssplit

import aiofiles
from aiofiles.os import mkdir, remove as aioremove
from aiohttp import ClientSession
from pyrogram import Client, filters
from telegraph.aio import Telegraph

LOGGER = logging.getLogger(__name__)

# Initialize Telegraph client for the bot
telegraph = Telegraph()

# ── section emoji map ────────────────────────────────────────────────────────
_SECTIONS = {"General": "🗒", "Video": "🎞", "Audio": "🔊", "Text": "🔠", "Menu": "🗃"}


async def cmd_exec(cmds):
    """Executes a shell command asynchronously and returns stdout, stderr, and return code."""
    process = await asyncio.create_subprocess_exec(
        *cmds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode('utf-8', 'replace').strip(),
        stderr.decode('utf-8', 'replace').strip(),
        process.returncode
    )


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
        # Create Telegraph account on the fly if it hasn't been created yet
        if not telegraph.get_access_token():
            await telegraph.create_account(short_name="MediaInfo")

        folder = "Mediainfo/"
        if not os.path.isdir(folder):
            await mkdir(folder)

        if link:
            filename = re_search(r".+/(.+)", link)
            filename = filename.group(1) if filename else "file"
            des_path = os.path.join(folder, filename)
            headers = {
                "user-agent": (
                    "Mozilla/5.0 (Linux; Android 12; 2201116PI) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/107.0.0.0 Mobile Safari/537.36"
                )
            }
            async with ClientSession() as session:
                async with session.get(link, headers=headers) as resp:
                    async with aiofiles.open(des_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(10_000_000):
                            await f.write(chunk)
                            break  # first chunk only — enough for mediainfo

        elif media:
            des_path = os.path.join(folder, media.file_name or "media_file")
            if media.file_size <= 50_000_000:
                await media_msg.download(file_name=os.path.join(os.getcwd(), des_path))
            else:
                # stream first ~5 MB so mediainfo can read headers
                async for chunk in client.stream_media(media_msg, limit=5):
                    async with aiofiles.open(des_path, "ab") as f:
                        await f.write(chunk)

        # Execute mediainfo using our built-in cmd_exec
        stdout, stderr, rc = await cmd_exec(ssplit(f'mediainfo "{des_path}"'))
        if rc != 0 or not stdout:
            raise RuntimeError(stderr or "mediainfo returned no output. Is mediainfo installed on your system?")

        title    = f"📌 {os.path.basename(des_path)}"
        content  = f"<h4>{title}</h4><br><br>" + _parse_mediainfo(stdout)
        
        # Create the page with Author Name and Link
        page = await telegraph.create_page(
            title="MediaInfo", 
            html_content=content,
            author_name="Goutham Josh",
            author_url="https://t.me/im_goutham_josh"
        )
        
        # graph.org is often preferred in bots over telegra.ph
        graph_url = f"https://graph.org/{page['path']}"
        
        await status.edit_text(
            f"<b>MediaInfo:</b>\n\n➲ <b>Link:</b> {graph_url}",
            disable_web_page_preview=False,
        )

    except Exception as exc:
        LOGGER.error(exc)
        await status.edit_text(f"<b>Error:</b> {exc}")
    finally:
        if des_path and os.path.exists(des_path):
            await aioremove(des_path)


@Client.on_message(filters.command(["mediainfo", "mi"]))
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
