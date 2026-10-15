"""
Telegram Mini App backend for KuttuBot.

Routes (mounted by plugins/webcode.py):
  GET  /app               -> miniapp/index.html
  POST /app/api/search    -> {init_data, query, offset}  -> movies (grouped, with posters)
  POST /app/api/movie     -> {init_data, key, q}         -> one movie's files + poster/details
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
MOVIE_MAX_PAGES = 3             # so at most 300 files per movie/series
MAX_SEND = 20                   # max files per send request
SEND_COOLDOWN = 3               # seconds between send requests per user
_last_send = {}                 # user_id -> monotonic time of last send request

_REGEX_META = re.compile(r'[\\^$.*+?{}\[\]|()]')


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


@routes.post("/app/api/search")
async def api_search(request):
    auth, resp = await _auth(request)
    if resp is not None:
        return resp
    _, body = auth

    query = _clean_query(body.get("query"))
    try:
        offset = max(0, int(body.get("offset", 0)))
    except (TypeError, ValueError):
        offset = 0

    files, next_offset, total = await get_search_results(
        query, max_results=PAGE_SIZE, offset=offset, filter=True
    )

    # group the page's files by movie / series, keeping first-seen (newest first) order
    groups = {}
    for f in files:
        p = parse_name(f.file_name)
        groups.setdefault(p["key"], p)

    infos = await get_infos([(p["title"], p["year"], p["kind"]) for p in groups.values()])
    movies = []
    for p, info in zip(groups.values(), infos):
        info = info or {}
        movies.append({
            "key": p["key"],
            "q": p["title"],                       # search text that finds this movie's files
            "title": info.get("title") or p["title"],
            "year": info.get("year") or p["year"],
            "kind": p["kind"],
            "thumb": info.get("thumb"),
            "rating": info.get("rating"),
        })
    return web.json_response({
        "ok": True,
        "movies": movies,
        "next_offset": next_offset if next_offset != "" else None,
        "total": total,
    })


@routes.post("/app/api/movie")
async def api_movie(request):
    """All files of one movie/series, plus poster and details."""
    auth, resp = await _auth(request)
    if resp is not None:
        return resp
    _, body = auth

    key = str(body.get("key") or "")[:200]
    q = _clean_query(body.get("q"))
    if not key or not q:
        return _err("Missing movie")

    matched, offset = [], 0
    for _ in range(MOVIE_MAX_PAGES):
        files, next_offset, _total = await get_search_results(
            q, max_results=MOVIE_PAGE_SIZE, offset=offset, filter=True
        )
        matched += [f for f in files if parse_name(f.file_name)["key"] == key]
        if next_offset == "" or not files:
            break
        offset = next_offset

    if not matched:
        return web.json_response({"ok": True, "info": None, "files": []})

    p = parse_name(matched[0].file_name)
    info = await get_info(p["title"], p["year"], p["kind"])
    if p["kind"] == "series":
        matched.sort(key=lambda f: f.file_name.lower())
    return web.json_response({
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
    })


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
