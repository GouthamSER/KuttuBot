import os
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from info import IMDB_TEMPLATE
from utils import extract_user, get_file_id, get_poster, fetch_poster_bytes
import time
from datetime import datetime
from io import BytesIO
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
        first = message.from_user.first_name
        last = message.from_user.last_name or ""
        username = message.from_user.username
        dc_id = message.from_user.dc_id or ""
        await message.reply_text(
            f"<b>➲ First Name:</b> {first}\n<b>➲ Last Name:</b> {last}\n<b>➲ Username:</b> {username}\n<b>➲ Telegram ID:</b> <code>{user_id}</code>\n<b>➲ Data Centre:</b> <code>{dc_id}</code>",
            quote=True
        )

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        _id = ""
        _id += (
            "<b>➲ Chat ID</b>: "
            f"<code>{message.chat.id}</code>\n"
        )
        if message.reply_to_message:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
                "<b>➲ Replied User ID</b>: "
                f"<code>{message.reply_to_message.from_user.id if message.reply_to_message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message.reply_to_message)
        else:
            _id += (
                "<b>➲ User ID</b>: "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
            )
            file_info = get_file_id(message)
        if file_info:
            _id += (
                f"<b>{file_info.message_type}</b>: "
                f"<code>{file_info.file_id}</code>\n"
            )
        await message.reply_text(
            _id,
            quote=True
        )

@Client.on_message(filters.command(["info"]))
async def who_is(client, message):
    # https://github.com/SpEcHiDe/PyroGramBot/blob/master/pyrobot/plugins/admemes/whois.py#L19
    status_message = await message.reply_text(
        "`Fetching user info...`"
    )
    await status_message.edit(
        "`Processing user info...`"
    )
    from_user = None
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return
    if from_user is None:
        return await status_message.edit("no valid user_id / message specified")
    message_out_str = ""
    message_out_str += f"<b>➲First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesn't Have A Valid DP]"
    message_out_str += f"<b>➲Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲User Name:</b> @{username}\n"
    message_out_str += f"<b>➲User 𝖫𝗂𝗇𝗄:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"
    if message.chat.type in ((enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL)):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = (
                chat_member_p.joined_date or datetime.now()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲Joined this Chat on:</b> <code>"
                f"{joined_date}"
                "</code>\n"
            )
        except UserNotParticipant:
            pass
    chat_photo = from_user.photo
    if chat_photo:
        local_user_photo = await client.download_media(
            message=chat_photo.big_file_id
        )
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
    await status_message.delete()

@Client.on_message(filters.command(["imdb", 'search']))
async def imdb_search(client, message):
    if ' ' in message.text:
        k = await message.reply('🔍 Searching...')
        r, title = message.text.split(None, 1)
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await k.edit("❌ No results found on OMDb.")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title') or movie.get('name', 'Unknown')} - {movie.get('year') or (str(movie.get('release_date') or movie.get('first_air_date') or ''))[:4] or 'N/A'}",
                    callback_data=f"imdb#{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('🎬 Here is what I found:', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Give me a movie / series Name')

async def _send_photo_bytes_or_text(message, poster_url, caption, btn):
    """Last resort before giving up on a real photo: download the poster ourselves
    and upload the raw bytes. Only if that also fails do we send plain text — and
    even then with the preview disabled, so we never show Telegram's own low-res
    link-preview card as a stand-in for the poster."""
    raw = await fetch_poster_bytes(poster_url)
    if raw:
        try:
            photo = BytesIO(raw)
            photo.name = "poster.jpg"
            await message.reply_photo(photo=photo, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
            return
        except Exception as e:
            logger.exception(e)
    await message.reply(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)


@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot: Client, quer_y: CallbackQuery):
    i, movie_id = quer_y.data.split('#')
    data = await get_poster(query=movie_id, id=True)
    message = quer_y.message.reply_to_message or quer_y.message
    if not data:
        await quer_y.answer("❌ Could not fetch details.", show_alert=True)
        return

    def _tags(field):
        if not field or field == "N/A":
            return "N/A"
        return " ".join(f"#{p.strip().replace(' ', '_')}" for p in field.split(",") if p.strip())

    # underscore-prefixed so they don't collide with the **locals() spread below
    _aka_line = f"\n📝 Also Known As: {data['aka']}" if data.get("aka") and data["aka"] != "N/A" else ""
    _genre_tags = _tags(data["genres"])
    _language_tags = _tags(data["languages"])
    _country_tags = _tags(data["countries"])

    btn = [
            [
                InlineKeyboardButton(
                    text=f"🔗 {data.get('title')} on IMDb",
                    url=data['url'],
                )
            ]
        ]
    if data.get("trailers"):
        btn.append([
            InlineKeyboardButton(
                text="▶️ Watch Trailer",
                url=data["trailers"][-1],
            )
        ])
    caption = IMDB_TEMPLATE.format(
        query = data['title'],
        title = data['title'],
        votes = data['votes'],
        aka = data["aka"],
        aka_line = _aka_line,
        seasons = data["seasons"],
        box_office = data['box_office'],
        localized_title = data['localized_title'],
        kind = data['kind'],
        imdb_id = data["imdb_id"],
        cast = data["cast"],
        runtime = data["runtime"],
        countries = data["countries"],
        country_tags = _country_tags,
        certificates = data["certificates"],
        languages = data["languages"],
        language_tags = _language_tags,
        director = data["director"],
        writer = data["writer"],
        producer = data["producer"],
        composer = data["composer"],
        cinematographer = data["cinematographer"],
        music_team = data["music_team"],
        distributors = data["distributors"],
        release_date = data['release_date'],
        year = data['year'],
        genres = data['genres'],
        genre_tags = _genre_tags,
        poster = data['poster'],
        plot = data['plot'],
        rating = data['rating'],
        url = data['url'],
        **locals()
    )
    if data.get('poster'):
        try:
            await quer_y.message.reply_photo(photo=data['poster'], caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = data.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            try:
                await quer_y.message.reply_photo(photo=poster, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
            except Exception as e:
                logger.exception(e)
                await _send_photo_bytes_or_text(quer_y.message, data['poster'], caption, btn)
        except Exception as e:
            logger.exception(e)
            await _send_photo_bytes_or_text(quer_y.message, data['poster'], caption, btn)
        await quer_y.message.delete()
    else:
        await quer_y.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
    await quer_y.answer()
