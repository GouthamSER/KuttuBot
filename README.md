<p align="center">
  <img src="https://user-images.githubusercontent.com/97418751/212598655-d7637a29-cba8-4ed6-92a4-6534d394b0f7.jpg" alt="ᴋᴜᴛᴛᴜ ʙᴏᴛ™ Logo" width="180">
</p>

<h1 align="center">ᴋᴜᴛᴛᴜ ʙᴏᴛ™</h1>

<p align="center">
  A powerful Telegram auto-filter bot built with <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a><br>
  Index your channels · Serve files · Manage groups with ease
</p>

<p align="center">
  <a href="https://github.com/GouthamSER/KuttuBot/stargazers"><img src="https://img.shields.io/github/stars/GouthamSER/KuttuBot?style=flat-square&color=yellow" alt="Stars"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/fork"><img src="https://img.shields.io/github/forks/GouthamSER/KuttuBot?style=flat-square&color=orange" alt="Forks"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/"><img src="https://img.shields.io/github/repo-size/GouthamSER/KuttuBot?style=flat-square&color=green" alt="Size"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL-blue" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" alt="Python">
</p>

<p align="center">
  <a href="https://telegram.dog/im_goutham_josh"><img src="https://img.shields.io/badge/Telegram-Support%20Group-30302f?style=flat&logo=telegram" alt="Support"></a>
  <a href="https://telegram.dog/wudixh15"><img src="https://img.shields.io/badge/Telegram-Updates%20Channel-30302f?style=flat&logo=telegram" alt="Updates"></a>
</p>

---

## 🆕 New Here? Deploy in 5 Minutes

Never run a Telegram bot before? Follow this in order — nothing else needed first.

1. **Get a bot token** — message [@BotFather](https://telegram.dog/BotFather) on Telegram, send `/newbot`, follow the prompts. Copy the token it gives you (`BOT_TOKEN`).
2. **Get your API ID & Hash** — go to [my.telegram.org](https://my.telegram.org/apps), log in with your phone number, create an app. Copy `API_ID` and `API_HASH`.
3. **Get a free MongoDB database** — sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas), create a free (M0) cluster, click *Connect → Drivers*, copy the connection string as `DATABASE_URI`. Pick any name for `DATABASE_NAME`.
4. **Get your Telegram user ID** — message [@missrose_bot](https://telegram.dog/missrose_bot) with `/id`, or forward any message of yours to it. This number is your `ADMINS` value.
5. **Make a log channel** — create a private Telegram channel, add your bot as admin in it, get the channel's ID (forward a message from it to @missrose_bot). This is `LOG_CHANNEL`.
6. **(Optional) Add channels to index** — any channel with the files you want searchable. Add the bot as admin there too, note the channel ID(s) for `CHANNELS`.
7. **Pick a deploy method** below (Koyeb is the easiest one-click option) and paste in the values from steps 1–6 as environment variables.
8. Once it's running, DM your bot `/start` — you're live.

> IMDb search (`/imdb`) works out of the box, no key needed — see [IMDb Lookup](#-imdb-lookup) below.

---

## ✨ Features

| Feature | Status |
|---|---|
| Auto Filter | ✅ |
| Manual Filter | ✅ |
| IMDb Info & Search (no API key required) | ✅ |
| IMDb Trailer Button | ✅ |
| Inline Search | ✅ |
| Spelling Check & Suggestions | ✅ |
| Language & Quality Filters | ✅ |
| File Store with Auto-Delete | ✅ |
| Fast Broadcast to All Users | ✅ |
| Index Channels | ✅ |
| Admin Commands | ✅ |
| Group Connection via PM | ✅ |
| Ban / Unban Users & Chats | ✅ |
| User & Chat Statistics | ✅ |
| Protect Content | ✅ |
| Force Subscribe Channel Check | ✅ |
| Auto Approve Join Requests | ✅ |
| Per-Group Settings | ✅ |
| 24-Hour Auto Restart | ✅ |
| Bounded In-Memory Caches (no unbounded RAM growth) | ✅ |

---

## 🎬 IMDb Lookup

`/imdb <title>` and `/search <title>` are powered by two sources, tried in order:

1. **[imdbio](https://pypi.org/project/imdbio/)** — scrapes IMDb directly, **no API key needed**, works immediately after `pip install`.
2. **[OMDb](https://www.omdbapi.com/apikey.aspx)** — used automatically as a fallback only if imdbio fails or is unreachable. Optional; set `OMDB_API_KEY` to enable it.

Result cards include title, year, rating, genre/language/country hashtags, storyline, and a **▶️ Watch Trailer** button when a trailer is available (imdbio only — OMDb has no trailer data).

---

## ⚙️ Configuration

Copy `sample_info.py` → `info.py` and fill in your values, **or** set them as environment variables for cloud deployments.

### 🔴 Required Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Get from [@BotFather](https://telegram.dog/BotFather) |
| `API_ID` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `CHANNELS` | Username or ID of channels to index (space-separated) |
| `ADMINS` | Username or ID of bot admins (space-separated) |
| `DATABASE_URI` | MongoDB connection URI — [get one free](https://www.mongodb.com) |
| `DATABASE_NAME` | Name of your MongoDB database |
| `LOG_CHANNEL` | Channel ID for bot activity logs (bot must be admin) |

### 🟡 Optional Variables

| Variable | Default | Description |
|---|---|---|
| `PICS` | Telegra.ph URLs | Space-separated image links shown on `/start` |
| `FILE_STORE_CHANNEL` | — | Channel IDs for file store links (space-separated) |
| `AUTH_CHANNEL` | — | Force-subscribe channel ID |
| `AUTH_USERS` | — | Extra user IDs with admin access |
| `AUTH_GROUP` | — | Allowed group IDs (space-separated) |
| `CACHE_TIME` | `300` | Inline query cache time (seconds) |
| `CUSTOM_FILE_CAPTION` | Script default | Caption template for sent files |
| `BATCH_FILE_CAPTION` | Built-in | Caption used in batch file links |
| `IMDB_TEMPLATE` | Built-in | Template for IMDb result messages (title, aka, rating, hashtags, storyline) |
| `IMDB` | `False` | Show IMDb info on search results |
| `LONG_IMDB_DESCRIPTION` | `False` | Use full plot instead of short summary |
| `OMDB_API_KEY` | — | Optional. Free key from [omdbapi.com](https://www.omdbapi.com/apikey.aspx), used only as a fallback if imdbio fails |
| `SINGLE_BUTTON` | `True` | Show filename + size in one button |
| `P_TTI_SHOW_OFF` | `True` | Redirect users to bot PM instead of sending file in group |
| `SPELL_CHECK_REPLY` | `True` | Suggest similar titles when file not found |
| `MAX_LIST_ELM` | `None` | Limit cast/crew list length in IMDb template |
| `PROTECT_CONTENT` | `False` | Enable forward-protection on sent files |
| `PUBLIC_FILE_STORE` | `False` | Allow any user to create file store links |
| `MELCOW_NEW_USERS` | `True` | Send welcome message to new users |
| `AUTO_DELETE_TIME` | `180` | Seconds before delivered files auto-delete (0 disables) |
| `COLLECTION_NAME` | `Telegram_files` | MongoDB collection name for indexed files |
| `INDEX_REQ_CHANNEL` | `LOG_CHANNEL` | Channel where index requests are logged |

> Full list with defaults: [`info.py`](./info.py) · Example config: [`sample_info.py`](./sample_info.py)

---

## 🚀 Deploy

### ☁️ Koyeb (Recommended)

<a href="https://app.koyeb.com/deploy?type=git&repository=github.com/GouthamSER/KuttuBot&branch=main&name=kuttubot">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb">
</a>

### ☁️ Scalingo

<a href="https://dashboard.scalingo.com/create/app?source=https://github.com/GouthamSER/KuttuBot">
  <img src="https://cdn.scalingo.com/deploy/button.svg" alt="Deploy to Scalingo">
</a>

### 🟣 Heroku

<details>
<summary>Click to expand</summary>
<br>
<a href="https://telegram.dog/XTZ_HerokuBot?start=QU0tUk9CT1RTL0V2YU1hcmlhIG1haW4">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku">
</a>
</details>

### 🐳 Docker

<details>
<summary>Click to expand</summary>

```bash
git clone https://github.com/GouthamSER/KuttuBot
cd KuttuBot
# Set your variables in info.py or as environment vars
docker-compose up -d
```

`Dockerfile` and `docker-compose.yml` are included in the repo.
</details>

### 🖥️ VPS / Self-Host

<details>
<summary>Click to expand</summary>

```bash
# Requires Python 3.10+
git clone https://github.com/GouthamSER/KuttuBot
cd KuttuBot
pip3 install -U -r requirements.txt
cp sample_info.py info.py
# Edit info.py with your values
python3 bot.py
```
</details>

---

## 📋 Commands

Set these in [@BotFather](https://telegram.dog/BotFather) → *Edit Bot* → *Edit Commands* so they show up in the Telegram command menu. Admin-only commands are marked and best left **out** of the public BotFather list — they're already gated in code so non-admins can't run them anyway.

### 👤 User Commands

| Command | Description |
|---|---|
| `/start` | Start the bot / get a file |
| `/imdb` | Search a movie or series on IMDb |
| `/search` | Same as `/imdb` |
| `/id` | Get your Telegram ID or a replied user/file's ID |
| `/info` | Get detailed info about a user |
| `/mediainfo` | Get technical mediainfo of a file |
| `/mi` | Same as `/mediainfo` |
| `/movies` | Browse latest movies |
| `/series` | Browse latest series |
| `/ping` | Check if the bot is alive |
| `/usage` | Show bot resource usage |

### 🔧 Filter & Connection Commands

| Command | Description |
|---|---|
| `/filter` | Add a manual filter (group admins) |
| `/add` | Same as `/filter` |
| `/filters` | View all filters in this chat |
| `/viewfilters` | Same as `/filters` |
| `/del` | Delete a specific filter |
| `/delall` | Delete all filters |
| `/connect` | Connect a group to your PM |
| `/disconnect` | Disconnect from current group |
| `/connections` | List your active connections |
| `/settings` | Configure per-group settings |
| `/set_template` | Set custom file caption template |

### 🛡️ Admin Commands
*(gated by `ADMINS` in code — safe to leave off the public BotFather command list)*

| Command | Description |
|---|---|
| `/broadcast` | Broadcast a message to all users (reply to the message) |
| `/restart` | Restart the bot |
| `/link` | Create a shareable link for a single post |
| `/deleteall` | Delete all indexed files |
| `/delete` | Delete a specific indexed file |
| `/setskip` | Set how many files to skip while indexing |
| `/stats` | View database and file stats |
| `/users` | List all users |
| `/chats` | List all chats |
| `/logs` | Get recent error logs |
| `/ban` | Ban a user from the bot |
| `/unban` | Unban a user |
| `/invite` | Generate an invite link for a chat the bot is admin in |
| `/leave` | Make the bot leave a chat |
| `/disable` | Disable the bot in a chat |
| `/enable` | Re-enable the bot in a chat |
| `/channel` | List all connected channels |
| `/approve_on`, `/approve_off` | Toggle auto-approve of join requests |
| `/welcome_on`, `/welcome_off` | Toggle welcome message on approval |
| `/approve_status` | Check current auto-approve settings |

> To index a channel: just **forward** a post from it (or paste its `t.me` link) to the bot in PM — no slash command needed. Batch links are generated from the same flow when you select a range of posts.

---

## 🗂️ Project Structure

```
KuttuBot/
├── bot.py                  # Entry point & Bot class
├── info.py                 # All configuration variables
├── sample_info.py          # Config template (copy → info.py)
├── utils.py                # Shared async utilities + imdbio/OMDb IMDb lookup
├── Script.py                # All message texts & templates
├── requirements.txt        # Python dependencies (includes imdbio)
├── Dockerfile               # Docker container config
├── docker-compose.yml       # Docker Compose config
├── plugins/
│   ├── pm_filter.py        # Auto filter, Language & Quality callbacks
│   ├── filters.py          # Manual filter management
│   ├── broadcast.py        # Fast broadcast system
│   ├── index.py            # Channel indexing
│   ├── inline.py           # Inline search
│   ├── connection.py       # PM ↔ group connection
│   ├── commands.py         # Start, help, file store & user commands
│   ├── channel.py          # Channel media handler
│   ├── misc.py             # ID, info, IMDb commands
│   ├── auto_approve.py     # Auto join request approval
│   ├── banned.py           # Banned user/chat middleware
│   ├── mov_ser_latest.py   # Latest movies & series listing
│   └── etc.py               # Extra/miscellaneous commands
└── database/
    ├── ia_filterdb.py      # Indexed file database (with bounded search cache)
    ├── filters_mdb.py      # Manual filter database
    ├── users_chats_db.py   # Users & chats database
    └── connections_mdb.py  # PM–group connection database
```

---

## 🔄 Recent Improvements

- 🎬 **IMDb without an API key** — added [imdbio](https://pypi.org/project/imdbio/) as the primary IMDb source (no key required); OMDb now only runs as a fallback when imdbio fails
- ▶️ **Trailer button** — IMDb result cards now show a "Watch Trailer" button when a trailer is available
- 🏷️ **New IMDb card layout** — hashtag genre/language/country, Also-Known-As line, matches the richer info-card style
- 🧠 **Memory leak fixes** — `BATCH_FILES` cache was growing unbounded across uptime, now capped at 250 entries like the rest of the in-memory caches; two `_SEARCH_CACHE` writes that bypassed the size-cap eviction now go through it properly
- 🔗 **`/invite` re-enabled** — the handler existed but its command decorator was commented out; wired back up as admin-only
- 🧹 **More dead code removed** — dropped unused imports (`last_online`, bare `import pyrogram`, `AUTH_GROUPS`, `search_gagala`) left over from earlier refactors
- ⚡ **Auto-filter speed** — `get_settings` and `get_search_results` now run in parallel via `asyncio.gather`; typing action fires as a background task so the DB query starts instantly
- 🗑️ **Cleaned filter buttons** — removed Years, Seasons, Episodes and Send All; only Language & Quality filters remain
- 🔍 **Search cache** — repeated queries within 60 s return instantly from memory (no DB round-trip)
- ⚡ **Broadcast speed** — removed per-user 2-second delay; broadcasts are now ~40× faster
- 🔧 **FloodWait fix** — updated `e.x` → `e.value` for Pyrogram v2+ compatibility
- 🌐 **Async HTTP** — replaced blocking `requests` library with `aiohttp`/`httpx` for non-blocking searches
- 🐛 **Search result bug** — fixed crash when regex fails in `get_search_results()` (wrong return type)
- 📦 **Inline search fix** — removed deprecated `pyrogram.emoji` import that caused startup crash

---

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) by **Dan** — the MTProto library powering this bot
- [imdbio](https://pypi.org/project/imdbio/) by **rjriajul** — key-free IMDb data source
- [EvaMaria](https://github.com/ritheshrkrm) by **Mahesh & Ritesh** — original bot base
- [TroJanZ](https://github.com/trojanzhex) — [AutoFilterBot](https://github.com/trojanzhex/auto-filter-bot) base
- [Goutham Josh](https://gouthamjosh.vercel.app) — repo maintainer, features & bug fixes
- Everyone who starred, forked, and contributed 💙

---

## ⚠️ Disclaimer

[![GNU AGPL v3](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html)

Licensed under [GNU AGPL v3.0](./LICENSE).

> **Selling this code for money is strictly prohibited.**
> Forking for personal use is welcome — please credit the original authors and do not rebrand as your own work. Respect the community that built this. 🙏
