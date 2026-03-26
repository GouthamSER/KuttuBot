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

## ✨ Features

| Feature | Status |
|---|---|
| Auto Filter | ✅ |
| Manual Filter | ✅ |
| IMDB Info & Search | ✅ |
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
| `IMDB_TEMPLATE` | Built-in | Template for IMDB result messages |
| `IMDB` | `False` | Show IMDB info on search results |
| `LONG_IMDB_DESCRIPTION` | `False` | Use full plot instead of short summary |
| `SINGLE_BUTTON` | `True` | Show filename + size in one button |
| `P_TTI_SHOW_OFF` | `True` | Redirect users to bot PM instead of sending file in group |
| `SPELL_CHECK_REPLY` | `True` | Suggest similar titles when file not found |
| `MAX_LIST_ELM` | `None` | Limit cast/crew list length in IMDB template |
| `PROTECT_CONTENT` | `False` | Enable forward-protection on sent files |
| `PUBLIC_FILE_STORE` | `False` | Allow any user to create file store links |
| `MELCOW_NEW_USERS` | `True` | Send welcome message to new users |
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

### 👤 User Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/help` | Get help info |
| `/about` | About the bot |
| `/id` | Get your Telegram ID |
| `/info` | Get info about a user |
| `/imdb` | Search a movie on IMDB |

### 🔧 Filter & Connection Commands

| Command | Description |
|---|---|
| `/filter` | Add a manual filter |
| `/filters` | View all filters in this group |
| `/del` | Delete a specific filter |
| `/delall` | Delete all filters |
| `/connect` | Connect a group to your PM |
| `/disconnect` | Disconnect from current group |
| `/connections` | List your active connections |
| `/settings` | Configure per-group settings |

### 🛡️ Admin Commands

| Command | Description |
|---|---|
| `/broadcast` | Broadcast a message to all users |
| `/index` | Index files from a channel |
| `/deleteall` | Delete all indexed files |
| `/delete` | Delete a specific indexed file |
| `/stats` | View database and file stats |
| `/users` | List all users |
| `/chats` | List all chats |
| `/logs` | Get recent error logs |
| `/batch` | Create a shareable link for multiple posts |
| `/link` | Create a shareable link for a single post |
| `/ban` | Ban a user from the bot |
| `/unban` | Unban a user |
| `/leave` | Make the bot leave a chat |
| `/disable` | Disable the bot in a chat |
| `/enable` | Re-enable the bot in a chat |
| `/channel` | List all connected channels |

---

## 🗂️ Project Structure

```
KuttuBot/
├── bot.py                  # Entry point & Bot class
├── info.py                 # All configuration variables
├── sample_info.py          # Config template (copy → info.py)
├── utils.py                # Shared async utilities
├── Script.py               # All message texts & templates
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container config
├── docker-compose.yml      # Docker Compose config
├── plugins/
│   ├── pm_filter.py        # Auto filter, Language & Quality callbacks
│   ├── filters.py          # Manual filter management
│   ├── broadcast.py        # Fast broadcast system
│   ├── index.py            # Channel indexing
│   ├── inline.py           # Inline search
│   ├── connection.py       # PM ↔ group connection
│   ├── commands.py         # Start, help, file store & user commands
│   ├── channel.py          # Channel media handler
│   ├── misc.py             # ID, info, IMDB commands
│   ├── auto_approve.py     # Auto join request approval
│   ├── banned.py           # Banned user/chat middleware
│   ├── mov_ser_latest.py   # Latest movies & series listing
│   └── etc.py              # Extra/miscellaneous commands
└── database/
    ├── ia_filterdb.py      # Indexed file database (with search cache)
    ├── filters_mdb.py      # Manual filter database
    ├── users_chats_db.py   # Users & chats database
    └── connections_mdb.py  # PM–group connection database
```

---

## 🔄 Recent Improvements

- ⚡ **Auto-filter speed** — `get_settings` and `get_search_results` now run in parallel via `asyncio.gather`; typing action fires as a background task so the DB query starts instantly
- 🗑️ **Cleaned filter buttons** — removed Years, Seasons, Episodes and Send All; only Language & Quality filters remain
- 🧹 **Dead code removed** — ~300 lines of unused handlers and data lists eliminated from `pm_filter.py`
- 🔍 **Search cache** — repeated queries within 60 s return instantly from memory (no DB round-trip)
- ⚡ **Broadcast speed** — removed per-user 2-second delay; broadcasts are now ~40× faster
- 🔧 **FloodWait fix** — updated `e.x` → `e.value` for Pyrogram v2+ compatibility
- 🌐 **Async HTTP** — replaced blocking `requests` library with `aiohttp` for non-blocking searches
- 🐛 **Search result bug** — fixed crash when regex fails in `get_search_results()` (wrong return type)
- 📦 **Inline search fix** — removed deprecated `pyrogram.emoji` import that caused startup crash

---

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) by **Dan** — the MTProto library powering this bot
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
