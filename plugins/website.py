"""
Public website for KuttuBot.

Routes (mounted by plugins/webcode.py):
  GET  /                -> site/index.html  (single page, hash routing)
  GET  /health          -> "ok"             (uptime / health checks)
  GET  /api/config      -> {bot, name}
  GET  /api/search      -> ?q=&offset=      -> movie cards (grouped, posters)
  POST /api/movie       -> {keys, qs}       -> one movie's files + details

Files are never downloaded from the site. A file button opens https://t.me/<bot>?start=wf_<token>
and the bot sends the file there (so ban list, force-subscribe and auto-delete all
keep working). The site never exposes Telegram file_ids: each file is given a short
token, stored in Mongo, and the bot turns the token back into the file on /start.
"""
import time
import hashlib
import logging
from pathlib import Path
from collections import defaultdict, deque

from aiohttp import web

from database.ia_filterdb import db, get_file_details
from plugins.miniapp import search_core, movie_core
from utils import temp

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()

SITE_FILE = Path(__file__).resolve().parent.parent / "site" / "index.html"

RATE_LIMIT = 60          # requests ...
RATE_WINDOW = 60         # ... per this many seconds, per IP
TOKEN_TTL = 14 * 24 * 3600
_hits = defaultdict(deque)
_tokens_ready = False


def _ip(request):
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() if fwd else request.remote) or "?"


def _limited(request):
    """True when this IP is over its rate limit."""
    now = time.monotonic()
    q = _hits[_ip(request)]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        return True
    q.append(now)
    if len(_hits) > 5000:                      # forget idle IPs
        for ip in [k for k, v in _hits.items() if not v or now - v[-1] > RATE_WINDOW]:
            _hits.pop(ip, None)
    return False


def _err(msg, status=400):
    return web.json_response({"ok": False, "error": msg}, status=status)


def _token(file_id: str) -> str:
    return hashlib.sha1(file_id.encode()).hexdigest()[:16]


async def _ensure_index():
    global _tokens_ready
    if _tokens_ready:
        return
    try:
        await db.web_tokens.create_index("ts", expireAfterSeconds=TOKEN_TTL)
    except Exception:
        logger.exception("web_tokens ttl index failed")
    _tokens_ready = True


async def _save_tokens(files):
    """Remember token -> file_id for the files shown on a movie page."""
    try:
        from pymongo import UpdateOne
        from datetime import datetime
        await _ensure_index()
        now = datetime.utcnow()
        ops = [UpdateOne({"_id": f["token"]}, {"$set": {"fid": f["_fid"], "ts": now}}, upsert=True) for f in files]
        if ops:
            await db.web_tokens.bulk_write(ops, ordered=False)
    except Exception:
        logger.exception("saving web tokens failed")


async def resolve_token(token: str):
    """token -> Telegram file_id (or None). Used by the /start handler."""
    if not token or len(token) > 32 or not token.isalnum():
        return None
    try:
        doc = await db.web_tokens.find_one({"_id": token})
    except Exception:
        logger.exception("web token lookup failed")
        return None
    return doc.get("fid") if doc else None


# ── Routes ─────────────────────────────────────────────────────────────────────
@routes.get("/", allow_head=True)
async def site_page(request):
    try:
        html = SITE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return web.json_response("KuttuBot is running")          # site files not deployed: keep health checks green
    return web.Response(text=html, content_type="text/html", headers={"Cache-Control": "no-cache"})


@routes.get("/health", allow_head=True)
async def health(request):
    return web.Response(text="ok")


@routes.get("/api/config")
async def api_config(request):
    return web.json_response({"bot": temp.U_NAME or "", "name": temp.B_NAME or "KuttuBot"},
                             headers={"Cache-Control": "public, max-age=300"})


@routes.get("/api/search")
async def api_search(request):
    if _limited(request):
        return _err("Too many requests, slow down a little", 429)
    try:
        data = await search_core(request.query.get("q", ""), request.query.get("offset", 0))
    except Exception:
        logger.exception("site search failed")
        return _err("Database is busy. Try again.", 500)
    return web.json_response(data)


@routes.post("/api/movie")
async def api_movie(request):
    if _limited(request):
        return _err("Too many requests, slow down a little", 429)
    try:
        body = await request.json()
    except Exception:
        return _err("Bad request")
    if not isinstance(body, dict):
        return _err("Bad request")
    try:
        data = await movie_core(body)
    except Exception:
        logger.exception("site movie failed")
        return _err("Could not load files right now.", 500)
    if data is None:
        return _err("Missing movie")
    files = []
    for f in data["files"]:
        files.append({"token": _token(f["id"]), "_fid": f["id"], "name": f["name"], "size": f["size"]})
    await _save_tokens(files)
    data["files"] = [{"id": f["token"], "name": f["name"], "size": f["size"]} for f in files]
    return web.json_response(data)
