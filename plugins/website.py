"""
Public website for KuttuBot.

Routes (mounted by plugins/webcode.py):
  GET  /                -> site/index.html  (single page, hash routing)
  GET  /m/<slug>        -> same page, short share link for a movie   (e.g. /m/the-paradise-2026)
  GET  /s/<slug>        -> same page, short share link for a series  (e.g. /s/money-heist)
  GET  /health          -> "ok"             (uptime / health checks)
  GET  /api/config      -> {bot, name}
  GET  /api/search      -> ?q=&offset=      -> movie cards (grouped, posters)
  POST /api/movie       -> {keys, qs}       -> one movie's files + details

Files are never downloaded from the site. A file button opens https://telegram.dog/<bot>?start=wf_<token>
and the bot sends the file there (so ban list, force-subscribe and auto-delete all
keep working). The site never exposes Telegram file_ids: each file is given a short
token, stored in Mongo, and the bot turns the token back into the file on /start.
"""
import re
import time
import asyncio
import hashlib
from html import escape
import logging
from pathlib import Path
from collections import defaultdict, deque

from aiohttp import web

from database.ia_filterdb import db, get_file_details
from plugins.miniapp import search_core, movie_core
from plugins.posters import get_info
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


async def clear_tokens():
    """Delete every website token. Called on bot start, so a restart leaves no old links behind."""
    try:
        res = await db.web_tokens.delete_many({})
        logger.info(f"website tokens cleared on start: {res.deleted_count}")
    except Exception:
        logger.exception("clearing website tokens failed")


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


_BOT_UA = re.compile(r"telegrambot|whatsapp|facebookexternalhit|twitterbot|discordbot|slackbot|linkedinbot|skypeuripreview", re.I)
_SLUG_YEAR = re.compile(r"^(.+)-((?:19|20)\d{2})$")


@routes.get("/m/{slug}", allow_head=True)
@routes.get("/s/{slug}", allow_head=True)
async def share_page(request):
    """Short share link. Serves the same single page; the page resolves the slug itself.
    Adds title / poster tags so Telegram, WhatsApp etc. show a proper link preview."""
    try:
        html = SITE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise web.HTTPNotFound()
    kind = "series" if request.path.startswith("/s/") else "movie"
    slug = re.sub(r"[^a-z0-9-]", "", request.match_info["slug"].lower())[:100]
    m = _SLUG_YEAR.match(slug) if kind == "movie" else None
    title = (m.group(1) if m else slug).replace("-", " ").strip().title()
    year = m.group(2) if m else ""
    if title:
        image = ""
        if _BOT_UA.search(request.headers.get("User-Agent", "")):      # only link-preview crawlers wait for the poster
            try:
                info = await asyncio.wait_for(get_info(title, year, kind), 2.5)
                image = (info or {}).get("poster") or (info or {}).get("thumb") or ""
            except Exception:
                image = ""
        label = f"{title} ({year})" if year else title
        tags = (
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="KuttuBot">'
            f'<meta property="og:title" content="{escape(label)} — KuttuBot">'
            f'<meta property="og:description" content="Poster, details and files for {escape(label)}. Get it in Telegram with one tap.">'
            + (f'<meta property="og:image" content="{escape(image)}"><meta name="twitter:card" content="summary_large_image">' if image else "")
        )
        html = html.replace("</head>", tags + "</head>", 1)
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
    resp = web.json_response(data, headers={"Cache-Control": "public, max-age=60"})
    resp.enable_compression()
    return resp


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
    resp = web.json_response(data)
    resp.enable_compression()
    return resp
