import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, USE_IMDBIO
from imdb import Cinemagoer
import imdbio
from imdbio import TitleType
import asyncio
from pyrogram.types import Message, InlineKeyboardButton
from pyrogram import enums
from typing import Union
import re
import os
from datetime import datetime
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import aiohttp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = Cinemagoer()

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# temp db for banned 
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT=int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    SETTINGS = {}

async def is_subscribed(bot, query):
    try:
        await bot.get_chat(int(AUTH_CHANNEL))  # resolve peer first
        user = await bot.get_chat_member(int(AUTH_CHANNEL), query.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True
    return False

class _ImdbioFakeMovie:
    """Wraps an imdbio MovieBriefInfo search result to match Cinemagoer's object interface."""
    def __init__(self, m):
        self._m = m
        # m.imdbId already carries the 'tt' prefix, e.g. 'tt0133093'
        self.movieID = f"imdbio_{m.imdbId}"
    def get(self, k, default=None):
        _map = {'title': 'title', 'year': 'year', 'kind': 'kind'}
        return getattr(self._m, _map.get(k, k), default)


def _cat_names(movie, key):
    """Pull a job-category (writer/producer/composer/...) name list off a MovieDetail."""
    people = (movie.categories or {}).get(key, [])
    return list_to_str([p.name for p in people]) if people else "N/A"


async def _imdbio_search(title, year=None, bulk=False):
    """Search imdbio (no API key needed). Returns list (_ImdbioFakeMovie) for bulk, or full dict."""
    try:
        year_int = int(year) if year else None
        result = await asyncio.to_thread(
            imdbio.search_title,
            title,
            year_int,
            False,
            None,
            (TitleType.Movies, TitleType.Series),
        )
    except Exception as e:
        logger.exception(f"imdbio search error: {e}")
        return None

    if not result or not result.titles:
        return None
    if bulk:
        return [_ImdbioFakeMovie(t) for t in result.titles[:10]]
    # fetch full details for top result
    imdb_id = result.titles[0].imdbId
    return await _imdbio_get_details(imdb_id) if imdb_id else None


async def _imdbio_get_details(imdb_id):
    """Fetch full imdbio details by IMDb ID (accepts with or without 'tt' prefix)."""
    try:
        movie = await asyncio.to_thread(imdbio.get_movie, imdb_id)
    except Exception as e:
        logger.exception(f"imdbio details error: {e}")
        return None
    if not movie:
        return None

    plot = movie.plot or "N/A"
    if not LONG_IMDB_DESCRIPTION and plot and len(plot) > 800:
        plot = plot[:800] + "..."
    kind = "tv series" if movie.is_series() else "movie"
    seasons = None
    info_series = getattr(movie, "info_series", None)
    if info_series and info_series.display_seasons:
        seasons = len(info_series.display_seasons)
    box_office = (movie.box_office or {}).get("grossWorldwide") or movie.worldwide_gross or "N/A"
    runtime = f"{movie.duration} min" if movie.duration else "N/A"

    return {
        'title': movie.title or "N/A",
        'votes': movie.votes if movie.votes is not None else "N/A",
        "aka": list_to_str(movie.title_akas),
        "seasons": seasons,
        "box_office": box_office,
        'localized_title': movie.title_localized or movie.title or "N/A",
        'kind': kind,
        "imdb_id": movie.imdbId or "N/A",
        "cast": list_to_str([p.name for p in movie.stars]),
        "runtime": runtime,
        "countries": list_to_str(movie.countries),
        "certificates": movie.certificate or "N/A",
        "languages": list_to_str(movie.languages_text or movie.languages),
        "director": list_to_str([p.name for p in movie.directors]),
        "writer": _cat_names(movie, "writer"),
        "producer": _cat_names(movie, "producer"),
        "composer": _cat_names(movie, "composer"),
        "cinematographer": _cat_names(movie, "cinematographer"),
        "music_team": _cat_names(movie, "music_department"),
        "distributors": "N/A",
        'release_date': movie.release_date or str(movie.year or "N/A"),
        'year': movie.year if movie.year is not None else "N/A",
        'genres': list_to_str(movie.genres),
        'poster': movie.cover_url,
        'plot': plot,
        'rating': str(movie.rating) if movie.rating is not None else "N/A",
        'url': movie.url or f"https://www.imdb.com/title/{movie.imdbId}/",
        '_source': 'imdbio',
    }


async def get_poster(query, bulk=False, id=False, file=None):
    # ── Direct ID lookups ────────────────────────────────────────────────────
    if id:
        if isinstance(query, str) and query.startswith("imdbio_"):
            # format: imdbio_tt1234567
            imdb_id = query[len("imdbio_"):]  # strip "imdbio_" prefix
            return await _imdbio_get_details(imdb_id)
        # plain IMDb numeric ID → use IMDb detail fetch
        return await _imdb_get_details(query)

    # ── Parse title + year ───────────────────────────────────────────────────
    query = (query.strip()).lower()
    title = query
    year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
    if year:
        year = list_to_str(year[:1])
        title = (query.replace(year, "")).strip()
    elif file is not None:
        year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
    else:
        year = None

    # ── imdbio primary (no API key needed) ───────────────────────────────────
    if USE_IMDBIO:
        imdbio_result = await _imdbio_search(title, year=year, bulk=bulk)
        if imdbio_result:
            return imdbio_result
        logger.info(f"imdbio no results for '{title}', trying Cinemagoer IMDb fallback")

    # ── IMDb fallback ────────────────────────────────────────────────────────
    try:
        movieid = imdb.search_movie(title.lower(), results=10)
    except Exception as e:
        logger.exception(f"IMDb search error: {e}")
        return None

    if not movieid:
        return None

    if year:
        filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
        if not filtered:
            filtered = movieid
    else:
        filtered = movieid
    filtered = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered)) or filtered

    if bulk:
        return filtered

    return await _imdb_get_details(filtered[0].movieID)


async def _imdb_get_details(movieid):
    """Fetch full IMDb details by movieID and return poster-compatible dict."""
    try:
        movie = imdb.get_movie(movieid)
    except Exception as e:
        logger.exception(f"IMDb get_movie error: {e}")
        return None

    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."

    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}',
        '_source': 'imdb',
    }
# https://github.com/odysseusmax/animated-lamp/blob/2ef4730eb2b5f0596ed6d03e7b05243d93e3415b/bot/utils/broadcast.py#L37

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"

async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    async with aiohttp.ClientSession(headers=usr_agent) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
    soup = BeautifulSoup(html, 'html.parser')
    titles = soup.find_all('h3')
    return [title.getText() for title in titles]


async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings
    
async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)
    
def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]  

def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name

    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
           
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            # don't want to make a request -_-
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)

def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'
