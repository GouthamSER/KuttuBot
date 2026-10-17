"""
Telegram Mini App backend for KuttuBot.

Routes (mounted by plugins/webcode.py):
  GET  /app               -> miniapp/index.html
  POST /app/api/search    -> {init_data, query, offset}  -> movies (grouped, with posters)
  POST /app/api/movie     -> {init_data, keys, qs}       -> one movie's files + poster/details
  POST /app/api/send      -> {init_data, ids:[file_id..]} -> sends files to user's PM

Every API call is authenticated with Telegram WebApp `initData` (HMAC-SHA256
signed with the bot token), so only real Telegram users opening the app from
this bot can call it.
"""
import hmac
import json
import time
import hashlib
import logging
import asyncio
import re
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qsl

from aiohttp import web

from info import BOT_TOKEN, AUTH_CHANNEL, AUTO_DELETE_TIME
from database.ia_filterdb import get_search_results, get_file_details
from utils import temp, get_size, is_subscribed, get_settings
from plugins.posters import parse_name, get_info, get_infos

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

INDEX_FILE = Path(__file__).resolve().parent.parent / "miniapp" / "index.html"

INIT_DATA_MAX_AGE = 24 * 3600   # seconds initData stays valid
PAGE_SIZE = 30                  # files fetched per search page (grouped into movies)
MOVIE_PAGE_SIZE = 100           # files per DB page when loading one movie
MOVIE_MAX_PAGES = 3             # DB pages read per search text when loading one movie
MOVIE_MAX_FILES = 300           # cap on files shown for one movie/series
SEARCH_MAX_PAGES = 3            # extra pages read when a page has no video titles
MAX_KEYS = 6                    # filename variants merged into one movie
MAX_SEND = 20                   # max files per send request
SEND_COOLDOWN = 3               # seconds between send requests per user
_last_send = {}                 # user_id -> monotonic time of last send request

_REGEX_META = re.compile(r'[\\^$.*+?{}\[\]|()]')


def _norm(s):
    return re.sub(r'[^a-z0-9]+', '', (s or '').lower())


def _years_compatible(a, b):
    return not a or not b or a == b


# ── Auth ───────────────────────────────────────────────────────────────────────
def validate_init_data(init_data: str, bot_token: str = BOT_TOKEN, max_age: int = INIT_DATA_MAX_AGE):
    """Return the Telegram user dict if initData is genuine and fresh, else None."""
    if not init_data or not bot_token:
        return None
    try:
        pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        return None

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError:
        return None
    if time.time() - auth_date > max_age:
        return None

    try:
        user = json.loads(pairs.get("user", ""))
    except Exception:
        return None
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):
        return None
    return user


def _clean_query(q) -> str:
    q = str(q or "")[:100]
    q = _REGEX_META.sub(" ", q)          # search runs as a regex; strip metachars
    return " ".join(q.split())


async def _read_json(request):
    try:
        data = await request.json()
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _err(msg, status=400):
    return web.json_response({"ok": False, "error": msg}, status=status)


async def _auth(request):
    """Return (user, body) or (None, error_response)."""
    body = await _read_json(request)
    if body is None:
        return None, _err("Bad request")
    user = validate_init_data(body.get("init_data", ""))
    if not user:
        return None, _err("Open this app from the bot in Telegram", 401)
    if user["id"] in temp.BANNED_USERS:
        return None, _err("You are banned from using this bot", 403)
    return (user, body), None


# ── Routes ─────────────────────────────────────────────────────────────────────
@routes.get("/app", allow_head=True)
async def app_page(request):
    try:
        html = INDEX_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return web.Response(text="Mini app files missing (miniapp/index.html)", status=500)
    return web.Response(
        text=html,
        content_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


def _offset(v):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return 0


async def search_core(query, offset=0):
    """Grouped movie cards for a search text (shared by the Mini App and the public website)."""
    query = _clean_query(query)
    offset = _offset(offset)

    # Fetch until we have at least one video title (a page can be all subtitles / audio files).
    groups, cursor = {}, offset
    next_offset, total = "", 0
    for _ in range(SEARCH_MAX_PAGES):
        files, next_offset, total = await get_search_results(
            query, max_results=PAGE_SIZE, offset=cursor, filter=True
        )
        for f in files:
            p = parse_name(f.file_name)
            if p["is_video"]:                       # subtitles / audio / archives only show inside a movie page
                groups.setdefault(p["key"], p)
        if groups or next_offset == "" or not files:
            break
        cursor = next_offset

    infos = await get_infos([(p["title"], p["year"], p["kind"]) for p in groups.values()])

    # Different filenames can be the same movie ("Khalifa The Ruler (2026)" and "Khalifa 2026").
    # Cards that resolve to the same IMDb title are merged into one.
    movies, by_ident = [], {}
    for p, info in zip(groups.values(), infos):
        info = info or {}
        ident = info.get("imdb_id") or (f"t:{_norm(info['title'])}" if info.get("source") and info.get("title") else "")
        target = next((m for m in by_ident.get(ident, []) if _years_compatible(m["_year"], p["year"])), None) if ident else None
        if target:
            if p["key"] not in target["keys"] and len(target["keys"]) < MAX_KEYS:
                target["keys"].append(p["key"])
            if p["title"] not in target["qs"] and len(target["qs"]) < MAX_KEYS:
                target["qs"].append(p["title"])
            if not target["thumb"] and info.get("thumb"):
                target["thumb"] = info["thumb"]
            continue
        m = {
            "mkey": f"{ident}|{p['year']}" if ident else p["key"],   # identity used to de-duplicate across pages
            "key": p["key"], "keys": [p["key"]],
            "q": p["title"], "qs": [p["title"]],      # search texts that find this movie's files
            "title": info.get("title") or p["title"],
            "year": info.get("year") or p["year"],
            "kind": p["kind"],
            "thumb": info.get("thumb"),
            "rating": info.get("rating"),
            "_year": p["year"],
        }
        movies.append(m)
        if ident:
            by_ident.setdefault(ident, []).append(m)
    for m in movies:
        m.pop("_year")
    return {
        "ok": True,
        "movies": movies,
        "next_offset": next_offset if next_offset != "" else None,
        "total": total,
    }


@routes.post("/app/api/search")
async def api_search(request):
    auth, resp = await _auth(request)
    if resp is not None:
        return resp
    _, body = auth
    return web.json_response(await search_core(body.get("query"), body.get("offset", 0)))


def _str_list(v, single=None, clean=False):
    """Accept a list (or one legacy string) from the client; return up to MAX_KEYS unique short strings."""
    items = v if isinstance(v, list) else [single]
    out = []
    for x in items:
        x = _clean_query(x) if clean else str(x or "")[:200]
        if x and x not in out:
            out.append(x)
    return out[:MAX_KEYS]


async def movie_core(body):
    """All files of one movie/series (every filename variant of it), plus poster and details.
    Returns a dict, or None when the request names no movie."""
    keys = _str_list(body.get("keys"), body.get("key"))
    qs = _str_list(body.get("qs"), body.get("q"), clean=True)
    if not keys or not qs:
        return None
    keyset = set(keys)

    # Poster/details lookup starts now and runs while the database is searched.
    # keys[0] is "<normalized title>|<year>" (movie) or "<normalized title>" (series).
    g_year = keys[0].split("|", 1)[1] if "|" in keys[0] else ""
    g_kind = "movie" if "|" in keys[0] else "series"
    info_task = asyncio.ensure_future(get_info(qs[0], g_year, g_kind, detail=True))

    async def fetch(q):
        out, offset = [], 0
        for _ in range(MOVIE_MAX_PAGES):
            files, next_offset, _total = await get_search_results(
                q, max_results=MOVIE_PAGE_SIZE, offset=offset, filter=True
            )
            out += [f for f in files if parse_name(f.file_name)["key"] in keyset]
            if next_offset == "" or not files:
                break
            offset = next_offset
        return out

    try:
        batches = await asyncio.gather(*(fetch(q) for q in qs))      # every filename variant at once
    except Exception:
        info_task.cancel()
        raise

    matched, seen_ids, seen_sig = [], set(), set()
    for batch in batches:
        for f in batch:
            # the same file indexed twice (two channels) has a different file_id but the same name + size
            sig = (" ".join(f.file_name.lower().split()), f.file_size)
            if f.file_id in seen_ids or sig in seen_sig:
                continue
            seen_ids.add(f.file_id)
            seen_sig.add(sig)
            matched.append(f)
    matched = matched[:MOVIE_MAX_FILES]

    if not matched:
        info_task.cancel()
        return {"ok": True, "info": None, "files": []}

    lead = next((f for f in matched if parse_name(f.file_name)["key"] == keys[0]), matched[0])
    p = parse_name(lead.file_name)
    try:
        info = await info_task
    except Exception:
        info = {}
    info = info or {}
    if p["kind"] == "series":
        matched.sort(key=lambda f: f.file_name.lower())
    return {
        "ok": True,
        "info": {
            "title": info.get("title") or p["title"],
            "year": info.get("year") or p["year"],
            "kind": p["kind"],
            "poster": info.get("poster"),
            "thumb": info.get("thumb"),
            "rating": info.get("rating"),
            "genres": info.get("genres") or [],
            "plot": info.get("plot") or "",
            "runtime": info.get("runtime") or "",
        },
        "files": [{"id": f.file_id, "name": f.file_name, "size": get_size(f.file_size)} for f in matched],
    }


@routes.post("/app/api/movie")
async def api_movie(request):
    auth, resp = await _auth(request)
    if resp is not None:
        return resp
    _, body = auth
    data = await movie_core(body)
    return _err("Missing movie") if data is None else web.json_response(data)


@routes.post("/app/api/send")
async def api_send(request):
    auth, resp = await _auth(request)
    if resp is not None:
        return resp
    user, body = auth
    user_id = user["id"]

    ids = body.get("ids")
    if not isinstance(ids, list) or not ids:
        return _err("No files selected")
    ids = [i for i in dict.fromkeys(ids) if isinstance(i, str) and 0 < len(i) <= 512][:MAX_SEND]
    if not ids:
        return _err("No valid files selected")

    now = time.monotonic()
    if now - _last_send.get(user_id, 0) < SEND_COOLDOWN:
        return _err("Slow down, try again in a few seconds", 429)
    _last_send[user_id] = now

    bot = request.app["bot"]

    # force-subscribe, same rule the bot uses
    if AUTH_CHANNEL:
        fake = SimpleNamespace(from_user=SimpleNamespace(id=user_id))
        if not await is_subscribed(bot, fake):
            return _err("Join the update channel first, then try again", 403)

    # lazy import: pm_filter is a pyrogram plugin, avoid import cycles at startup
    from plugins.pm_filter import _send_selected_file, _auto_delete_file
    from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

    settings = await get_settings(user_id)
    sent = 0
    for fid in ids:
        docs = await get_file_details(fid)
        if not docs:
            continue
        try:
            msg = await _send_selected_file(bot, user_id, docs[0], settings)
        except (UserIsBlocked, PeerIdInvalid):
            return _err("Start the bot in Telegram first (send /start), then retry", 403)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                msg = await _send_selected_file(bot, user_id, docs[0], settings)
            except Exception:
                continue
        except Exception:
            logger.exception("miniapp send failed")
            continue
        sent += 1
        asyncio.create_task(_auto_delete_file(bot, msg))

    if not sent:
        return _err("Could not send the files", 500)
    return web.json_response({
        "ok": True, "sent": sent, "requested": len(ids), "delete_after": AUTO_DELETE_TIME,
    })
