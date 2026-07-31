import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, TMDB_API_KEY
import imdbinfo
from imdbinfo import search_title as imdbinfo_search_title, get_movie as imdbinfo_get_movie, TitleType
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
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

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
    """Wraps an imdbinfo MovieBriefInfo search result to match Cinemagoer's object interface."""
    def __init__(self, m):
        self._m = m
        # m.imdb_id already carries the 'tt' prefix, e.g. 'tt0133093'
        self.movieID = f"imdbio_{m.imdb_id}"
    def get(self, k, default=None):
        _map = {'title': 'title', 'year': 'year', 'kind': 'kind'}
        return getattr(self._m, _map.get(k, k), default)

TMDB_IMG_BASE = "https://image.tmdb.org/t/p/original"

class _TmdbFakeMovie:
    """Wraps a TMDB search result to match Cinemagoer's object interface."""
    def __init__(self, m):
        self._m = m
        self.movieID = f"tmdb_{m.get('id')}"
    def get(self, k, default=None):
        _map = {'title': 'title', 'year': 'year', 'kind': 'media_type'}
        key = _map.get(k, k)
        if key == 'title':
            return self._m.get('title') or self._m.get('name') or default
        if key == 'year':
            d = self._m.get('release_date') or self._m.get('first_air_date') or ''
            return d[:4] if d else default
        return self._m.get(key, default)


async def _tmdb_search(title, year=None, bulk=False):
    """Fallback search via TMDB (used when imdbio is blocked/down)."""
    if not TMDB_API_KEY:
        logger.warning("TMDB_API_KEY not set, skipping tmdb fallback")
        return None
    try:
        params = {"api_key": TMDB_API_KEY, "query": title, "include_adult": "false"}
        if year:
            params["year"] = year
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.themoviedb.org/3/search/multi", params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception(f"tmdb search error: {e}")
        return None

    results = [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
    if not results:
        return None
    if bulk:
        return [_TmdbFakeMovie(r) for r in results[:10]]
    return await _tmdb_get_details(results[0]["id"], results[0]["media_type"])


async def _tmdb_get_details(tmdb_id, media_type="movie"):
    """Fetch full TMDB details by id + media_type ('movie' or 'tv')."""
    if not TMDB_API_KEY:
        return None
    try:
        params = {"api_key": TMDB_API_KEY, "append_to_response": "credits"}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}", params=params)
            resp.raise_for_status()
            m = resp.json()
    except Exception as e:
        logger.exception(f"tmdb details error: {e}")
        return None
    if not m:
        return None

    credits = m.get("credits", {})
    cast = list_to_str([c.get("name") for c in credits.get("cast", [])[:10]])
    directors = list_to_str([c.get("name") for c in credits.get("crew", []) if c.get("job") == "Director"])
    writers = list_to_str([c.get("name") for c in credits.get("crew", []) if c.get("job") in ("Writer", "Screenplay")])
    title = m.get("title") or m.get("name") or "N/A"
    release_date = m.get("release_date") or m.get("first_air_date") or "N/A"
    year = release_date[:4] if release_date and release_date != "N/A" else "N/A"
    plot = m.get("overview") or "N/A"
    if not LONG_IMDB_DESCRIPTION and plot and len(plot) > 800:
        plot = plot[:800] + "..."
    poster_path = m.get("poster_path")

    return {
        'title': title,
        'votes': m.get("vote_count", "N/A"),
        "aka": "N/A",
        "seasons": m.get("number_of_seasons"),
        "box_office": "N/A",
        'localized_title': title,
        'kind': "tv series" if media_type == "tv" else "movie",
        "imdb_id": "N/A",
        "cast": cast or "N/A",
        "runtime": f"{m.get('runtime')} min" if m.get("runtime") else "N/A",
        "countries": list_to_str([c.get("name") for c in m.get("production_countries", [])]),
        "certificates": "N/A",
        "languages": list_to_str([l.get("english_name") for l in m.get("spoken_languages", [])]),
        "director": directors or "N/A",
        "writer": writers or "N/A",
        "producer": "N/A",
        "composer": "N/A",
        "cinematographer": "N/A",
        "music_team": "N/A",
        "distributors": "N/A",
        'release_date': release_date,
        'year': year,
        'genres': list_to_str([g.get("name") for g in m.get("genres", [])]),
        'poster': f"{TMDB_IMG_BASE}{poster_path}" if poster_path else None,
        'plot': plot,
        'rating': str(m.get("vote_average", "N/A")),
        'url': f"https://www.themoviedb.org/{media_type}/{tmdb_id}",
        '_source': 'tmdb',
    }


def _first_attr(obj, *names, default=None):
    """Return first present, non-None attribute from a list of possible names."""
    for n in names:
        v = getattr(obj, n, None)
        if v is not None:
            return v
    return default


def _cat_names(movie, key):
    """Pull a job-category (writer/producer/composer/...) name list off a MovieDetail, if present."""
    categories = getattr(movie, "categories", None) or {}
    people = categories.get(key, [])
    return list_to_str([getattr(p, "name", str(p)) for p in people]) if people else "N/A"


async def _imdbio_search(title, year=None, bulk=False, _retry=True):
    """Search imdb via imdbinfo (no API key needed). Falls back to tmdb on block/failure."""
    try:
        year_int = int(year) if year else None
        result = await asyncio.to_thread(
            imdbinfo_search_title,
            title,
            year_int,
            False,
            None,
            (TitleType.Movies, TitleType.Series),
        )
    except Exception as e:
        if "403" in str(e) and _retry:
            # blocked, back off once then fall through to tmdb
            await asyncio.sleep(1.5)
            return await _imdbio_search(title, year, bulk, _retry=False)
        logger.warning(f"imdbinfo search failed for '{title}': {e}, falling back to tmdb")
        return await _tmdb_search(title, year, bulk)

    if not result or not result.titles:
        return await _tmdb_search(title, year, bulk)
    if bulk:
        return [_ImdbioFakeMovie(t) for t in result.titles[:10]]
    # fetch full details for top result
    imdb_id = result.titles[0].imdb_id
    return await _imdbio_get_details(imdb_id) if imdb_id else await _tmdb_search(title, year, bulk)


async def _imdbio_get_details(imdb_id):
    """Fetch full details via imdbinfo by IMDb ID (accepts with or without 'tt' prefix)."""
    try:
        movie = await asyncio.to_thread(imdbinfo_get_movie, imdb_id)
    except Exception as e:
        logger.warning(f"imdbinfo details failed for '{imdb_id}': {e}, falling back to tmdb")
        return await _tmdb_get_details(str(imdb_id).lstrip("tt"), "movie")
    if not movie:
        return await _tmdb_get_details(str(imdb_id).lstrip("tt"), "movie")

    plot = getattr(movie, "plot", None) or "N/A"
    if not LONG_IMDB_DESCRIPTION and plot and len(plot) > 800:
        plot = plot[:800] + "..."
    kind = "tv series" if movie.is_series() else "movie"
    seasons = None
    info_series = getattr(movie, "info_series", None)
    if info_series and getattr(info_series, "display_seasons", None):
        seasons = len(info_series.display_seasons)
    box_office_raw = _first_attr(movie, "box_office", default={}) or {}
    box_office = (box_office_raw.get("grossWorldwide") if isinstance(box_office_raw, dict) else None) \
        or _first_attr(movie, "worldwide_gross", default="N/A")
    duration = _first_attr(movie, "duration", "runtime")
    runtime = f"{duration} min" if duration else "N/A"

    cast_list = _first_attr(movie, "stars", "cast", default=[]) or []
    directors_list = _first_attr(movie, "directors", "director", default=[]) or []
    genres_list = _first_attr(movie, "genres", default=[]) or []
    countries_list = _first_attr(movie, "countries", default=[]) or []
    languages_list = _first_attr(movie, "languages_text", "languages", default=[]) or []
    akas_list = _first_attr(movie, "title_akas", "akas", default=[]) or []

    return {
        'title': getattr(movie, "title", None) or "N/A",
        'votes': _first_attr(movie, "votes", "vote_count", default="N/A"),
        "aka": list_to_str(akas_list),
        "seasons": seasons,
        "box_office": box_office,
        'localized_title': getattr(movie, "title_localized", None) or getattr(movie, "title", None) or "N/A",
        'kind': kind,
        "imdb_id": getattr(movie, "imdb_id", None) or "N/A",
        "cast": list_to_str([getattr(p, "name", str(p)) for p in cast_list]) if cast_list else "N/A",
        "runtime": runtime,
        "countries": list_to_str(countries_list),
        "certificates": _first_attr(movie, "certificate", "certificates", default="N/A"),
        "languages": list_to_str(languages_list),
        "director": list_to_str([getattr(p, "name", str(p)) for p in directors_list]) if directors_list else "N/A",
        "writer": _cat_names(movie, "writer"),
        "producer": _cat_names(movie, "producer"),
        "composer": _cat_names(movie, "composer"),
        "cinematographer": _cat_names(movie, "cinematographer"),
        "music_team": _cat_names(movie, "music_department"),
        "distributors": "N/A",
        'release_date': getattr(movie, "release_date", None) or str(getattr(movie, "year", None) or "N/A"),
        'year': getattr(movie, "year", None) if getattr(movie, "year", None) is not None else "N/A",
        'genres': list_to_str(genres_list),
        'poster': _first_attr(movie, "cover_url", "poster_url", "poster"),
        'plot': plot,
        'rating': str(movie.rating) if getattr(movie, "rating", None) is not None else "N/A",
        'url': getattr(movie, "url", None) or f"https://www.imdb.com/title/{getattr(movie, 'imdb_id', imdb_id)}/",
        '_source': 'imdbinfo',
    }


async def get_poster(query, bulk=False, id=False, file=None):
    # ── Direct ID lookups ────────────────────────────────────────────────────
    if id:
        if isinstance(query, str) and query.startswith("tmdb_"):
            tmdb_id = query[len("tmdb_"):]
            return await _tmdb_get_details(tmdb_id, "movie") or await _tmdb_get_details(tmdb_id, "tv")
        imdb_id = query
        if isinstance(query, str) and query.startswith("imdbio_"):
            imdb_id = query[len("imdbio_"):]  # strip "imdbio_" prefix
        return await _imdbio_get_details(imdb_id)

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

    return await _imdbio_search(title, year=year, bulk=bulk)

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
