"""
Movie grouping + poster lookup for the Mini App.

  parse_name(file_name)  -> {"title", "year", "kind", "key"}   (from a release filename)
  get_info(title, year, kind, detail=False) -> dict with poster/thumb/rating/genres/plot (cached)

Poster source order (first one that has a poster wins, text gaps are filled from the others):
  1. imdbio  (IMDb via the imdbinfo library, no API key)
  2. OMDb    (IMDb data; needs OMDB_API_KEY)  - backup when imdbio is blocked/down
  3. TMDB    (optional; needs TMDB_API_KEY)   - last resort
Results are cached in memory, including misses, so a title costs at most one lookup a day.
"""
import re
import time
import asyncio
import logging

import httpx

from info import OMDB_API_KEY, TMDB_API_KEY

try:
    from imdbinfo import search_title as _imdb_search, get_movie as _imdb_get_movie, TitleType
except Exception:                        # library missing: skip imdbio, OMDb/TMDB still work
    _imdb_search = _imdb_get_movie = TitleType = None

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


# The bot stores names with "." "_" "-" turned into spaces ("Movie 2026 720p mkv"), so the
# extension may follow a space instead of a dot.
VIDEO_EXTS = ('mkv', 'mp4', 'avi', 'mov', 'm4v', 'webm', 'ts', 'wmv', 'flv', 'mpg', 'mpeg')
NON_VIDEO_EXTS = ('srt', 'ass', 'zip', 'rar', '7z', 'txt', 'nfo', 'mp3', 'flac', 'm4a', 'wav', 'ogg', 'opus',
                  'jpg', 'jpeg', 'png', 'pdf', 'apk')
_EXT = re.compile(r'[\s._-]+(' + '|'.join(VIDEO_EXTS + NON_VIDEO_EXTS) + r')$', re.I)


def parse_name(file_name: str) -> dict:
    """Best-effort movie/series title + year from a release filename.
    Also returns `ext` and `is_video` (subtitles, audio, archives are not video)."""
    raw = (file_name or '').strip()
    em = _EXT.search(raw)
    ext = em.group(1).lower() if em else ''
    if em:
        raw = raw[:em.start()]
    for _ in range(3):                                    # strip stacked leading tags like "[Tag] @chan -"
        new = _LEADING_TAGS.sub('', raw)
        if new == raw:
            break
        raw = new
    text = re.sub(r'[._+]+', ' ', raw)

    ep = _EPISODE.search(text)
    stop_for_year = ep.start() if ep else len(text)
    years = [m for m in _YEAR.finditer(text[:stop_for_year])]
    ym = years[0] if years else None
    # a year at the very start is part of the title ("1917", "2012")
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
    return {"title": title, "year": year, "kind": kind, "key": key,
            "ext": ext, "is_video": ext not in NON_VIDEO_EXTS}


# ── Poster lookup ──────────────────────────────────────────────────────────────
HIT_TTL = 24 * 3600
MISS_TTL = 3600
CACHE_MAX = 2000
HTTP_TIMEOUT = 6
IMDBIO_TIMEOUT = 10
_cache = {}           # cache_key -> (expires_at, info dict)
_inflight = {}        # cache_key -> asyncio.Task (dedupe concurrent lookups)
_sem = asyncio.Semaphore(6)
_TEXT_FIELDS = ("title", "year", "rating", "genres", "plot", "runtime", "imdb_id")


def _imdb_sizes(url):
    """IMDb images look like '...@._V1_SX300.jpg'. Dropping the size suffix gives the original;
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
        v = round(float(v), 1)
        return v or None
    except (TypeError, ValueError):
        return None


def _empty(title, year):
    return {"poster": None, "thumb": None, "source": None, "title": title, "year": year or "",
            "rating": None, "genres": [], "plot": "", "runtime": "", "imdb_id": ""}


# -- source 1: imdbio ----------------------------------------------------------
async def _imdbio(title, year, kind):
    if not _imdb_search:
        return None
    types = (TitleType.Series,) if kind == 'series' else (TitleType.Movies,)
    year_int = int(year) if (year and kind != 'series') else None

    async def search(y, retry=True):
        try:
            return await asyncio.to_thread(_imdb_search, title, y, False, None, types)
        except Exception as e:
            if "403" in str(e) and retry:                 # blocked: back off once
                await asyncio.sleep(1.5)
                return await search(y, retry=False)
            raise

    res = await search(year_int)
    if (not res or not res.titles) and year_int:          # filename year can be wrong
        res = await search(None)
    if not res or not res.titles:
        return None
    t = res.titles[0]
    full, thumb = _imdb_sizes(getattr(t, "cover_url", None))
    return {
        "poster": full, "thumb": thumb, "source": "imdbio",
        "title": getattr(t, "title", None) or title,
        "year": str(getattr(t, "year", None) or year or ""),
        "rating": _num(getattr(t, "rating", None)),
        "genres": [], "plot": "", "runtime": "",
        "imdb_id": getattr(t, "imdb_id", "") or "",
    }


async def _imdbio_details(imdb_id):
    """Plot / genres / runtime for one title (only needed on the movie page)."""
    if not _imdb_get_movie or not imdb_id:
        return None
    m = await asyncio.to_thread(_imdb_get_movie, imdb_id)
    if not m:
        return None
    dur = getattr(m, "duration", None)
    return {
        "plot": getattr(m, "plot", None) or "",
        "genres": [str(g) for g in (getattr(m, "genres", None) or [])],
        "runtime": f"{dur} min" if dur else "",
        "rating": _num(getattr(m, "rating", None)),
    }


# -- source 2: OMDb ------------------------------------------------------------
def _omdb_info(d, title, year):
    full, thumb = _imdb_sizes(d.get("Poster"))
    na = lambda v: v if v not in (None, "N/A") else ""
    return {
        "poster": full, "thumb": thumb, "source": "omdb",
        "title": d.get("Title") or title,
        "year": (d.get("Year") or year or "").split("–")[0],
        "rating": _num(d.get("imdbRating")),
        "genres": [g.strip() for g in na(d.get("Genre")).split(",") if g.strip()],
        "plot": na(d.get("Plot")), "runtime": na(d.get("Runtime")), "imdb_id": d.get("imdbID") or "",
    }


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
    return _omdb_info(d, title, year) if d.get("Response") == "True" else None


async def _omdb_by_id(client, imdb_id):
    if not OMDB_API_KEY or not imdb_id:
        return None
    r = await client.get("https://www.omdbapi.com/", params={"apikey": OMDB_API_KEY, "i": imdb_id, "plot": "short"})
    r.raise_for_status()
    d = r.json()
    return _omdb_info(d, "", "") if d.get("Response") == "True" else None


# -- source 3: TMDB (optional) -------------------------------------------------
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
        "rating": _num(m.get("vote_average")),
        "genres": [], "plot": m.get("overview") or "", "runtime": "", "imdb_id": "",
    }


# -- combine -------------------------------------------------------------------
def _merge(found):
    """found: results in priority order. Take the first with a poster; fill text gaps from the rest."""
    if not found:
        return None
    base = dict(next((f for f in found if f.get("poster")), found[0]))
    for other in found:
        for k in _TEXT_FIELDS:
            if not base.get(k) and other.get(k):
                base[k] = other[k]
    return base


async def _lookup(title, year, kind):
    async with _sem:
        found = []
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            async def omdb():
                r = await _omdb(client, title, year, kind)
                if not r and year:                         # filename year can be wrong
                    r = await _omdb(client, title, '', kind)
                return r
            steps = (
                ("imdbio", lambda: asyncio.wait_for(_imdbio(title, year, kind), IMDBIO_TIMEOUT)),
                ("omdb", omdb),
                ("tmdb", lambda: _tmdb(client, title, year, kind)),
            )
            for name, fn in steps:
                try:
                    r = await fn()
                except Exception as e:
                    logger.warning(f"{name} lookup failed for {title!r}: {e!r}")
                    r = None
                if r:
                    found.append(r)
                    if r.get("poster"):
                        break                              # poster found, no need to try further sources
        return _merge(found)


async def _enrich(info):
    """Add plot/genres/runtime (not in imdbio search results). imdbio first, OMDb as backup."""
    extra = None
    try:
        extra = await asyncio.wait_for(_imdbio_details(info.get("imdb_id")), IMDBIO_TIMEOUT)
    except Exception as e:
        logger.warning(f"imdbio details failed for {info.get('imdb_id')!r}: {e!r}")
    if not extra or not (extra.get("plot") or extra.get("genres")):
        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                extra = await _omdb_by_id(client, info.get("imdb_id")) or extra
        except Exception as e:
            logger.warning(f"omdb details failed for {info.get('imdb_id')!r}: {e!r}")
    out = dict(info)
    for k in ("plot", "genres", "runtime", "rating"):
        if extra and extra.get(k) and not out.get(k):
            out[k] = extra[k]
    return out


def _trim():
    if len(_cache) > CACHE_MAX:
        for k in sorted(_cache, key=lambda k: _cache[k][0])[:CACHE_MAX // 5]:
            _cache.pop(k, None)


async def _get_cached(title, year, kind):
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
        logger.warning(f"poster lookup crashed for {title!r}: {e!r}")
        info = None
    finally:
        if task.done():
            _inflight.pop(ck, None)
    if info is None:
        info, ttl = _empty(title, year), MISS_TTL
    else:
        ttl = HIT_TTL if info.get("poster") else MISS_TTL
    _cache[ck] = (time.time() + ttl, info)
    _trim()
    return info


async def get_info(title, year='', kind='movie', detail=False):
    """Cached poster/info lookup. Never raises; misses return an empty info dict.
    detail=True also fills plot/genres/runtime (one extra request, cached)."""
    info = await _get_cached(title, year, kind)
    if not detail or not info.get("imdb_id") or (info.get("plot") and info.get("genres")):
        return info
    dk = f"detail|{kind}|{re.sub(r'[^a-z0-9]+', '', title.lower())}|{year}"
    hit = _cache.get(dk)
    if hit and hit[0] > time.time():
        return hit[1]
    full = await _enrich(info)
    _cache[dk] = (time.time() + HIT_TTL, full)
    _trim()
    return full


async def get_infos(items, budget=3.0):
    """items: list of (title, year, kind). Resolve concurrently within `budget` seconds.
    Slow lookups keep running in the background (and fill the cache); their slots return None."""
    tasks = [asyncio.ensure_future(get_info(*it)) for it in items]
    if tasks:
        await asyncio.wait(tasks, timeout=budget)
    out = []
    for t in tasks:
        out.append(t.result() if t.done() and not t.cancelled() and t.exception() is None else None)
    return out
