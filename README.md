<p align="center">
  <img src="https://user-images.githubusercontent.com/97418751/212598655-d7637a29-cba8-4ed6-92a4-6534d394b0f7.jpg" alt="ᴋᴜᴛᴛᴜ ʙᴏᴛ™ Logo" width="170" style="border-radius: 50%;">
</p>

<h1 align="center">ᴋᴜᴛᴛᴜ ʙᴏᴛ™</h1>

<p align="center">
  <b>Enterprise-Grade, High-Performance Telegram Auto-Filter & Media Management Suite</b><br>
  <i>Powered by Pyrogram v2 & AsyncIO Motor MongoDB</i>
</p>

<p align="center">
  <a href="https://github.com/GouthamSER/KuttuBot/stargazers"><img src="https://img.shields.io/github/stars/GouthamSER/KuttuBot?style=for-the-badge&color=f5c518&logo=github" alt="Stars"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/network/members"><img src="https://img.shields.io/github/forks/GouthamSER/KuttuBot?style=for-the-badge&color=ff8000&logo=git" alt="Forks"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue?style=for-the-badge" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://docs.pyrogram.org/"><img src="https://img.shields.io/badge/Pyrogram-v2.0+-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Pyrogram"></a>
</p>

<p align="center">
  <a href="https://telegram.dog/im_goutham_josh"><img src="https://img.shields.io/badge/Telegram-Support%20Chat-2CA5E0?style=flat-square&logo=telegram" alt="Support Chat"></a>
  <a href="https://telegram.dog/wudixh15"><img src="https://img.shields.io/badge/Telegram-Developer-blueviolet?style=flat-square&logo=telegram" alt="Developer"></a>
  <a href="https://telegram.dog/wudixh1"><img src="https://img.shields.io/badge/Telegram-Updates%20Channel-0088cc?style=flat-square&logo=telegram" alt="Updates Channel"></a>
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start Guide](#-quick-start-guide)
- [Configuration Reference](#-configuration-reference)
  - [Required Environment Variables](#-required-environment-variables)
  - [Optional Customization Variables](#-optional-customization-variables)
- [Deployment Options](#-deployment-options)
  - [Koyeb](#-koyeb-one-click)
  - [Heroku & Scalingo](#-heroku--scalingo)
  - [Docker & Docker Compose](#-docker--docker-compose)
  - [Linux VPS / Self-Hosted](#-linux-vps--self-hosted)
- [Command Matrix](#-command-matrix)
  - [General User Commands](#-general-user-commands)
  - [Filter & Connection Management](#-filter--connection-management)
  - [Admin-Only Commands](#-admin-only-commands)
- [Project Architecture](#-project-architecture)
- [Recent Improvements & Bug Fixes](#-recent-improvements--bug-fixes)
- [Credits & Licensing](#-credits--licensing)

---

## 🌟 Overview

**ᴋᴜᴛᴛᴜ ʙᴏᴛ™** is an ultra-fast, modular Telegram bot designed for indexing Telegram channels, providing instant auto-filter search results, and managing large media libraries effortlessly.

Built from the ground up on modern asynchronous Python patterns, it features **in-memory search acceleration**, **multi-select batch delivery**, **Telegraph-powered technical MediaInfo generation**, **smart typo corrections**, and **built-in web server health checking** for 24/7 cloud uptime.

---

## ✨ Key Features

| Category | Highlights |
|---|---|
| 🔍 **Search & Filters** | Instant auto-filter with pagination, language filtering (Multi, Malayalam, Tamil, Hindi, Kannada, Telugu, English), and resolution quality filtering (4K, 1080p, 720p, etc.). |
| ☑️ **Batch & Multi-Select** | Multi-select files right from search results and receive them all in private chat with a single tap. |
| 🎬 **IMDb & Metadata** | Real-time movie/series cards with ratings, cast, genres, release dates, storylines, and **Watch Trailer** buttons — works out of the box with zero API keys required (via `imdbio`, with optional OMDb fallback). |
| 📊 **Technical MediaInfo** | Pass any media file or direct video link to `/mediainfo` (`/mi`) to generate a clean, formatted Telegraph inspection page with automatic 5-minute self-destruction. |
| 🛡️ **Group Management** | Remote connection via PM (`/connect`), per-group settings toggles, custom captions, custom welcome media, force-subscription verification, and auto-approval for channel join requests. |
| ⚡ **Performance & Stability** | Async Motor MongoDB driver, non-blocking concurrent queries via `asyncio.gather`, 60-second search query caching, memory-bounded dictionary caches, and a built-in `aiohttp` web server on port `8080` for Koyeb / Heroku health-checks. |

---

## ⚡ Quick Start Guide

Deploy your own instance of **KuttuBot** in less than 5 minutes:

1. **Create Bot on Telegram**:
   - Open [@BotFather](https://telegram.dog/BotFather) on Telegram and send `/newbot`.
   - Choose a display name and username. Save the generated `BOT_TOKEN`.

2. **Obtain Telegram API Credentials**:
   - Log into [my.telegram.org](https://my.telegram.org/apps) with your Telegram phone number.
   - Create an application to get your `API_ID` (integer) and `API_HASH` (string).

3. **Set Up MongoDB Database**:
   - Create a free cloud cluster on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   - Under *Database Access*, create a user and password.
   - Under *Network Access*, add `0.0.0.0/0` (allow from anywhere).
   - Under *Clusters → Connect → Drivers*, copy your connection string as `DATABASE_URI` (e.g. `mongodb+srv://...`).

4. **Identify Admin and Log Channel IDs**:
   - Message [@missrose_bot](https://telegram.dog/missrose_bot) with `/id` to get your personal numerical Telegram ID (`ADMINS`).
   - Create a private channel for bot logs, add your bot as an administrator with full permissions, and forward a message from that channel to `@missrose_bot` to get its channel ID (`LOG_CHANNEL`, starts with `-100`).

5. **Deploy & Launch**:
   - Choose any deployment option below, provide the required environment variables, and send `/start` to your bot in Telegram!

---

## ⚙️ Configuration Reference

Settings can be specified as environment variables (cloud hosts) or configured in `info.py` (local/VPS).

### 🔴 Required Environment Variables

| Variable | Description | Example / Format |
|---|---|---|
| `BOT_TOKEN` | Token generated by [@BotFather](https://telegram.dog/BotFather) | `7123456789:AAH...` |
| `API_ID` | Telegram API identifier from [my.telegram.org](https://my.telegram.org) | `12345678` |
| `API_HASH` | Telegram API hash from [my.telegram.org](https://my.telegram.org) | `0123456789abcdef0123456789abcdef` |
| `ADMINS` | Telegram user ID(s) of bot administrators (space-separated) | `123456789 987654321` |
| `DATABASE_URI` | MongoDB Atlas URI connection string | `mongodb+srv://user:pass@cluster...` |
| `DATABASE_NAME` | Name of the MongoDB database | `KuttuBot` |
| `LOG_CHANNEL` | Telegram Channel ID for logging bot activity | `-1001234567890` |
| `CHANNELS` | Channel IDs or usernames to index files from (space-separated) | `-1001987654321 -1001122334455` |

### 🟡 Optional Customization Variables

| Variable | Default | Description |
|---|---|---|
| `AUTH_CHANNEL` | `None` | Channel ID for Force-Subscribe (users must join to use the bot). |
| `AUTO_DELETE_TIME` | `180` | Delay in seconds before sent media files are auto-deleted from user PM (`0` to disable). |
| `OMDB_API_KEY` | `None` | Free API key from [omdbapi.com](https://www.omdbapi.com) (used as fallback when IMDb scraper is unreachable). |
| `PICS` | Telegraph URLs | Space-separated image URLs rotated randomly for the `/start` message. |
| `CUSTOM_FILE_CAPTION` | Built-in script | Caption template applied to individual files sent to users. |
| `BATCH_FILE_CAPTION` | Built-in script | Caption template applied to batch-delivered media files. |
| `IMDB` | `False` | Enable/disable IMDb info cards by default in search responses. |
| `LONG_IMDB_DESCRIPTION` | `False` | Show full plot synopsis instead of truncated summary. |
| `PROTECT_CONTENT` | `False` | Prevent forwarding and saving of delivered files by default. |
| `SINGLE_BUTTON` | `True` | Display filename and file size in a single compact button. |
| `P_TTI_SHOW_OFF` | `True` | Direct users to PM to collect files rather than cluttering groups. |
| `SPELL_CHECK_REPLY` | `True` | Display interactive spelling corrections when no exact match is found. |
| `MELCOW_NEW_USERS` | `True` | Send animated welcome media when new members join connected groups. |
| `CACHE_TIME` | `300` | Inline query caching duration in seconds. |
| `PORT` | `8080` | Port for the internal HTTP health check web server. |
| `AUTO_APPROVE` | `ON` | Automatically approve join requests for channels/groups where bot is admin. |
| `WELCOME_DM` | `OFF` | Send a private welcome message to users approved via join requests. |

---

## 🚀 Deployment Options

### ☁️ Koyeb (One-Click)

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/GouthamSER/KuttuBot&branch=main&name=kuttubot)

> [!TIP]
> KuttuBot includes a built-in `aiohttp` web server on port `8080` that binds to `0.0.0.0`, satisfying Koyeb's internal TCP health checks automatically.

### 🟣 Heroku / Scalingo

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/GouthamSER/KuttuBot)
[![Deploy to Scalingo](https://cdn.scalingo.com/deploy/button.svg)](https://dashboard.scalingo.com/create/app?source=https://github.com/GouthamSER/KuttuBot)

### 🐳 Docker & Docker Compose

Run isolated in a Docker container using the pre-configured `docker-compose.yml`:

```bash
# 1. Clone the repository
git clone https://github.com/GouthamSER/KuttuBot.git
cd KuttuBot

# 2. Configure variables in docker-compose.yml or create a .env file
cp sample_info.py info.py

# 3. Build and launch
docker-compose up -d --build
```

### 🖥️ Linux VPS / Self-Hosted

```bash
# 1. Update system packages and install MediaInfo
sudo apt update && sudo apt install -y python3 python3-pip mediainfo git

# 2. Clone repository
git clone https://github.com/GouthamSER/KuttuBot.git
cd KuttuBot

# 3. Install Python requirements
pip3 install -U -r requirements.txt

# 4. Create your configuration
cp sample_info.py info.py
nano info.py

# 5. Start bot
python3 bot.py
```

---

## 📋 Command Matrix

### 👤 General User Commands

| Command | Description |
|---|---|
| `/start` | Start bot, view main menu, or fetch media from deep links |
| `/imdb <title>` | Search movie or TV show information on IMDb with trailer button |
| `/search <title>` | Search database files and IMDb simultaneously |
| `/mediainfo` or `/mi` | Generate technical MediaInfo sheet for a replied file or direct URL |
| `/movies` | Browse recently added movies in the database |
| `/series` | Browse latest television series and available episodes |
| `/id` | Show Telegram ID, Chat ID, and media file IDs |
| `/info` | Retrieve comprehensive profile info and joined dates for any user |
| `/ping` | Measure real-time MTProto response latency and network quality |
| `/usage` | Display real-time CPU, RAM, Disk, and Koyeb/VPS server metrics |

### 🔧 Filter & Connection Management

| Command | Description |
|---|---|
| `/connect <chat_id>` | Connect a group to your private chat for remote management |
| `/disconnect` | Disconnect from the currently active group connection |
| `/connections` | View and toggle all active group connections |
| `/settings` | Open interactive button menu to configure group preferences |
| `/set_template <template>` | Set customized IMDb caption template for group responses |
| `/filter <keyword> <reply>` | Add a manual reply filter in the connected chat |
| `/filters` or `/viewfilters` | List all active manual keyword filters in the chat |
| `/del <keyword>` | Delete a specific manual filter |
| `/delall` | Delete all manual filters from the group (Owner / Admin only) |

### 🛡️ Admin-Only Commands

*(Restricted to user IDs specified in `ADMINS`)*

| Command | Description |
|---|---|
| `/broadcast` | Broadcast a message to all registered users (reply to target message) |
| `/index` | Forward last message or channel link to index files |
| `/setskip <number>` | Set message skip offset counter for bulk indexing |
| `/delete <reply>` | Remove a replied media file from the database |
| `/deleteall` | Drop all indexed file documents from the database |
| `/channel` | List all indexed channels and member counts |
| `/users` | Export comprehensive list of bot users with status |
| `/chats` | Export list of all registered groups and status |
| `/stats` | View real-time database collection size and storage quota |
| `/logs` | Send the current runtime application log file (`TelegramBot.log`) |
| `/ban <user_id> [reason]` | Ban a user from using the bot |
| `/unban <user_id>` | Revoke a user's ban status |
| `/disable <chat_id> [reason]` | Restrict and disable bot functionality in a chat |
| `/enable <chat_id>` | Re-enable bot functionality in a disabled chat |
| `/leave <chat_id>` | Instruct the bot to cleanly leave a group |
| `/invite <chat_id>` | Generate an invite link for any chat the bot administers |
| `/restart` | Restart the bot process gracefully |
| `/link <name>` | Generate a shareable Telegram deep link for a movie title |
| `/approve_on` / `/approve_off` | Toggle automatic join request approval |
| `/welcome_on` / `/welcome_off` | Toggle DM welcome notifications on join approval |
| `/approve_status` | View current status of join request approval engine |

---

## 🗂️ Project Architecture

```
KuttuBot/
├── bot.py                  # Core Bot client, scheduler, iter_messages & aiohttp web server
├── info.py                 # Central environment variable loader and config validation
├── sample_info.py          # Configuration template
├── Script.py               # UI text strings, markdown templates & help messages
├── utils.py                # Utilities, IMDb parser, poster byte fetcher & temp state
├── requirements.txt        # Python package dependencies
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Multi-container orchestration
├── logging.conf            # Logging formatter configurations
│
├── plugins/                # Modular Pyrogram Event Handlers
│   ├── pm_filter.py        # Auto-filter, multi-select, language/quality filters & callbacks
│   ├── commands.py         # Start, help, settings, channel info & batch file processing
│   ├── filters.py          # Manual custom keyword filters (/filter, /del, /delall)
│   ├── index.py            # Channel scraper and bulk database indexer
│   ├── inline.py           # Telegram inline query search provider
│   ├── connection.py       # PM-to-Group remote management bridge (/connect)
│   ├── mediainfo.py        # Technical MediaInfo parser & Telegraph publisher
│   ├── misc.py             # User lookup (/info), ID inspection (/id) & IMDb (/imdb)
│   ├── mov_ser_latest.py   # Recent movie & series catalog browser (/movies, /series)
│   ├── auto_approve.py     # Channel & group join request auto-approver
│   ├── broadcast.py        # High-throughput asynchronous mass broadcast engine
│   ├── banned.py           # Access control middleware for banned users and chats
│   ├── channel.py          # Real-time channel post listener & file saver
│   ├── etc.py              # System monitor (/usage), latency (/ping), link generator (/link)
│   └── webcode.py          # Aiohttp health-check HTTP endpoints
│
└── database/               # Asynchronous Motor MongoDB Layer
    ├── ia_filterdb.py      # File metadata schema, indexes, natural sorting & cached queries
    ├── filters_mdb.py      # Manual keyword filters storage
    ├── users_chats_db.py   # User accounts, group settings, bans & status registry
    └── connections_mdb.py  # User-to-Group active connection mapping
```

---

## 🔄 Recent Improvements & Bug Fixes

- 🛡️ **Comprehensive Admin ID Type Resolution**: Standardized `ADMINS` checking across all plugins ([commands.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/commands.py), [filters.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/filters.py), [connection.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/connection.py), [pm_filter.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/pm_filter.py)) to prevent integer vs string ID mismatch rejections.
- 🎬 **IMDb Without API Keys**: Integrated `imdbio` as primary metadata provider; OMDb acts purely as secondary fallback. Result cards display formatted hashtag genres and direct trailer buttons.
- 🗂️ **Channel Indexing Workflow Fix**: Fixed channel forward detection in [index.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/index.py) to prioritize forwarded channel posts and prevent invalid link errors. Fixed public link username crashes.
- 🔒 **Pagination Security Sync**: Corrected pagination button callback prefix in [pm_filter.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/pm_filter.py), ensuring `file_secure` content protection is preserved across all search pages.
- 🏷️ **Caption Attribute Safety**: Added safe `.html` extraction on media captions in [ia_filterdb.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/database/ia_filterdb.py) and [filters.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/filters.py), eliminating `AttributeError` crashes on media without captions.
- 🌐 **Inline Query Optimization**: Enforced 64-character limit on `switch_pm_text` in [inline.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/inline.py) to prevent Telegram API button data validation errors.
- 🖥️ **Cross-Platform MediaInfo Execution**: Eliminated Windows backslash escaping errors in [mediainfo.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/mediainfo.py) by passing arguments directly without shell token splitting.
- 📝 **UTF-8 Export Safety**: Added explicit UTF-8 encoding and automatic file cleanup for `/users` and `/chats` text exports in [p_ttishow.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/p_ttishow.py).
- ⚙️ **Auto-Approve Inverted Logic Fix**: Fixed boolean comparison in [auto_approve.py](file:///c:/Users/Goutham%20Josh/Downloads/KuttuBot-main/plugins/auto_approve.py) so default `"OFF"` correctly disables welcome DMs.

---

## 🙏 Credits

- [Dan](https://github.com/delivrance) for [Pyrogram](https://github.com/pyrogram/pyrogram)
- [Goutham Josh](https://gouthamjosh.vercel.app) for maintenance, features & optimization
- [rjriajul](https://github.com/rjriajul) for [imdbio](https://pypi.org/project/imdbio/)
- [TroJanZ](https://github.com/trojanzhex) & [EvaMaria](https://github.com/ritheshrkrm) teams for early auto-filter foundations
- All contributors, stargazers, and community members 💙

---

## ⚖️ License & Disclaimer

[![GNU AGPL v3](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html)

This project is open-source under the [GNU Affero General Public License v3.0](./LICENSE).

> **Commercial resale of this code is strictly prohibited.**
> You are free to fork, customize, and self-host for personal and non-commercial community use with proper attribution retained.
