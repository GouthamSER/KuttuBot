"""
Movie grouping + poster lookup for the Mini App.

  parse_name(file_name)  -> {"title", "year", "kind", "key"}   (from a release filename)
  get_info(title, year, kind) -> dict with poster/thumb/rating/genres/plot (cached)

Poster source order:
  1. OMDb  (IMDb data; needs OMDB_API_KEY)  - original-resolution IMDb poster
  2. TMDB  (optional; needs TMDB_API_KEY)   - only used when OMDb finds nothing
Both lookups are cached in memory, including misses, so a movie costs one API
call per day at most.
"""
import re
import time
import asyncio
import logging

import httpx

from info import OMDB_API_KEY, TMDB_API_KEY

logger = logging.getLogger(__name__)

# ── Filename -> title / year ───────────────────────────────────────────────────
_LEADING_TAGS = re.compile(r'^\s*(?:\[[^\]]*\]|\([^)]*\)|@\w+|www\.\S+?\.\w{2,4}\b)[\s._-]*', re.I)
_YEAR = re.compile(r'(?<![0-9])((?:19|20)\d{2})(?![0-9])')
_EPISODE = re.compile(r'\b(?:S\d{1,2}[\s._-]*E\d{1,3}|S\d{1,2}\b|E\d{2,3}\b|Season[\s._-]*\d+|Ep(?:isode)?[\s._-]*\d+)', re.I)
_JUNK = re.compile(
    r'\b(?:480p|576p|720p|1080p|1440p|2160p|4k|uhd|hdr|web[\s-]?dl|webrip|web|hdrip|hdtv|bluray|brrip|bdrip|dvdrip|'
    r'hdcam|camrip|cam|hdts|predvd|x264|x265|h\.?26[45]|hevc|10bit|aac|ac3|dd\+?\d?|ddp\d?|atmos|esubs?|msubs?|'
    r'dual|multi|proper|uncut|extended|org|true|amzn|nf|hotstar|zee5|sonyliv)\b', re.I)
_LANG = re.compile(r'\b(?:hindi|tamil|telugu|malayalam|kannada|english|bengali|marathi|punjabi)\b', re.I)


def _clean(s: str) -> str:
    s = re.sub(r'[._+]+', ' ', s)
    s = re.sub(r'\s+-\s+|\s*-\s*(?=\s|$)', ' ', s)
    return re.sub(r'\s+', ' ', s).strip(' -[]()')


def parse_name(file_name: str) -> dict:
    """Best-effort movie/series title + year from a release filename."""
    raw = re.sub(r'\.(mkv|mp4|avi|mov|m4v|webm|ts|zip|rar|srt)$', '', file_name or '', flags=re.I)
    for _ in range(3):                                    # strip stacked leading tags like "[Tag] @chan -"
        new = _LEADING_TAGS.sub('', raw)
        if new == raw:
            break
        raw = new
    text = re.sub(r'[._+]+', ' ', raw)

    ep = _EPISODE.search(text)
    # take the LAST plausible year before any episode marker, so "2012 (2009)" style names behave
    stop_for_year = ep.start() if ep else len(text)
    years = [m for m in _YEAR.finditer(text[:stop_for_year])]
    ym = years[0] if years else None
    # if the year is the very start of the name it is part of the title ("1917", "2012")
    if ym and ym.start() == 0 and len(years) > 1:
        ym = years[1]
    elif ym and ym.start() == 0:
        ym = None

    cuts = []
    if ep:
        cuts.append(ep.start())
    if ym:
        cuts.append(ym.start())
    j = _JUNK.search(text)
    if j:
        cuts.append(j.start())
    lang = _LANG.search(text)
    if lang and not ym and not ep:
        cuts.append(lang.start())

    title = _clean(text[:min(cuts)]) if cuts else _clean(text)
    if len(title) < 2:                                    # over-eager cut: fall back to year/episode cut only
        soft = [c for c in ([ep.start()] if ep else []) + ([ym.start()] if ym else [])]
        title = _clean(text[:min(soft)]) if soft else _clean(text)
    if not title:
        title = _clean(raw) or file_name

    kind = 'series' if ep else 'movie'
    year = ym.group(1) if (ym and kind == 'movie') else ''
    norm = re.sub(r'[^a-z0-9]+', '', title.lower())
    key = norm if kind == 'series' else f"{norm}|{year}"
    return {"title": title, "year": year, "kind": kind, "key": key}


# ── Poster lookup ──────────────────────────────────────────────────────────────
HIT_TTL = 24 * 3600
MISS_TTL = 3600
CACHE_MAX = 2000
HTTP_TIMEOUT = 6
_cache = {}           # cache_key -> (expires_at, info dict)
_inflight = {}        # cache_key -> asyncio.Task (dedupe concurrent lookups)
_sem = asyncio.Semaphore(6)


def _imdb_sizes(url):
    """OMDb gives '...@._V1_SX300.jpg'. Dropping the size suffix gives the original;
    adding our own gives a lighter thumbnail for grid cards."""
    if not url or url == 'N/A':
        return None, None
    base = re.sub(r'\._V1_[^/]*?(?=\.\w+$)', '', url)
    ext = re.search(r'\.\w+$', base)
    stem = base[:ext.start()] if ext else base
    suffix = ext.group(0) if ext else '.jpg'
    return base, f"{stem}._V1_SX500{suffix}"


def _num(v):
    try:
        return round(float(v), 1)
    except (TypeError, ValueError):
        return None


async def _omdb(client, title, year, kind):
    if not OMDB_API_KEY:
        return None
    params = {"apikey": OMDB_API_KEY, "t": title, "plot": "short",
              "type": "series" if kind == 'series' else "movie"}
    if year:
        params["y"] = year
    r = await client.get("https://www.omdbapi.com/", params=params)
    r.raise_for_status()
    d = r.json()
    if d.get("Response") != "True":
        return None
    full, thumb = _imdb_sizes(d.get("Poster"))
    return {
        "poster": full, "thumb": thumb, "source": "imdb",
        "title": d.get("Title") or title,
        "year": (d.get("Year") or year or "").split("–")[0],
        "rating": _num(d.get("imdbRating")),
        "genres": [g.strip() for g in (d.get("Genre") or "").split(",") if g.strip() and g.strip() != "N/A"],
        "plot": d.get("Plot") if d.get("Plot") not in (None, "N/A") else "",
        "runtime": d.get("Runtime") if d.get("Runtime") not in (None, "N/A") else "",
        "imdb_id": d.get("imdbID") or "",
    }


async def _tmdb(client, title, year, kind):
    if not TMDB_API_KEY:
        return None
    path = "search/tv" if kind == 'series' else "search/movie"
    params = {"api_key": TMDB_API_KEY, "query": title, "include_adult": "false"}
    if year:
        params["year" if kind != 'series' else "first_air_date_year"] = year
    r = await client.get(f"https://api.themoviedb.org/3/{path}", params=params)
    r.raise_for_status()
    results = r.json().get("results") or []
    results = [x for x in results if x.get("poster_path")] or results
    if not results:
        return None
    m = results[0]
    pp = m.get("poster_path")
    date = m.get("release_date") or m.get("first_air_date") or ""
    return {
        "poster": f"https://image.tmdb.org/t/p/original{pp}" if pp else None,
        "thumb": f"https://image.tmdb.org/t/p/w500{pp}" if pp else None,
        "source": "tmdb",
        "title": m.get("title") or m.get("name") or title,
        "year": date[:4] or year or "",
        "rating": _num(m.get("vote_average")) or None,
        "genres": [], "plot": m.get("overview") or "", "runtime": "", "imdb_id": "",
    }


def _empty(title, year):
    return {"poster": None, "thumb": None, "source": None, "title": title, "year": year or "",
            "rating": None, "genres": [], "plot": "", "runtime": "", "imdb_id": ""}


async def _lookup(title, year, kind):
    async with _sem:
        info = None
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            try:
                info = await _omdb(client, title, year, kind)
                if not info and year:                      # filename year can be wrong: retry without it
                    info = await _omdb(client, title, '', kind)
            except Exception as e:
                logger.warning(f"omdb lookup failed for {title!r}: {e}")
            if not info or not info.get("poster"):         # fallback only when OMDb has no poster
                try:
                    alt = await _tmdb(client, title, year, kind)
                except Exception as e:
                    logger.warning(f"tmdb lookup failed for {title!r}: {e}")
                    alt = None
                if alt and (not info or alt.get("poster")):
                    if info:                               # keep IMDb text, take TMDB poster
                        alt = {**alt, **{k: info[k] for k in ("title", "year", "rating", "genres", "plot", "runtime", "imdb_id") if info.get(k)},
                               "source": "imdb+tmdb"}
                    info = alt
        return info


def _trim():
    if len(_cache) > CACHE_MAX:
        for k in sorted(_cache, key=lambda k: _cache[k][0])[:CACHE_MAX // 5]:
            _cache.pop(k, None)


async def get_info(title, year='', kind='movie'):
    """Cached poster/info lookup. Never raises; misses return an empty info dict."""
    ck = f"{kind}|{re.sub(r'[^a-z0-9]+', '', title.lower())}|{year}"
    hit = _cache.get(ck)
    if hit and hit[0] > time.time():
        return hit[1]
    task = _inflight.get(ck)
    if task is None:
        task = asyncio.ensure_future(_lookup(title, year, kind))
        _inflight[ck] = task
    try:
        info = await asyncio.shield(task)
    except Exception as e:
        logger.warning(f"poster lookup crashed for {title!r}: {e}")
        info = None
    finally:
        if task.done():
            _inflight.pop(ck, None)
    if info is None:
        info = _empty(title, year)
        ttl = MISS_TTL
    else:
        ttl = HIT_TTL if info.get("poster") else MISS_TTL
    _cache[ck] = (time.time() + ttl, info)
    _trim()
    return info


async def get_infos(items, budget=5.0):
    """items: list of (title, year, kind). Resolve concurrently within `budget` seconds.
    Slow lookups keep running in the background (and fill the cache); their slots return None."""
    tasks = [asyncio.ensure_future(get_info(*it)) for it in items]
    if tasks:
        await asyncio.wait(tasks, timeout=budget)
    out = []
    for t in tasks:
        out.append(t.result() if t.done() and not t.cancelled() and t.exception() is None else None)
    return out
