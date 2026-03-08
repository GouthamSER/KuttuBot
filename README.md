<p align="center">
  <img src="https://user-images.githubusercontent.com/97418751/212598655-d7637a29-cba8-4ed6-92a4-6534d394b0f7.jpg" alt="ᴋᴜᴛᴛᴜ ʙᴏᴛ™ Logo" width="200">
</p>

<h1 align="center">ᴋᴜᴛᴛᴜ ʙᴏᴛ™</h1>

<p align="center">
  A powerful Telegram auto-filter bot built with <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a> — index your channels, serve files, and manage your groups with ease.
</p>

<p align="center">
  <a href="https://github.com/GouthamSER/KuttuBot/stargazers"><img src="https://img.shields.io/github/stars/GouthamSER/KuttuBot?style=flat-square&color=yellow" alt="Stars"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/fork"><img src="https://img.shields.io/github/forks/GouthamSER/KuttuBot?style=flat-square&color=orange" alt="Forks"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/"><img src="https://img.shields.io/github/repo-size/GouthamSER/KuttuBot?style=flat-square&color=green" alt="Size"></a>
  <a href="https://github.com/GouthamSER/KuttuBot"><img src="https://badges.frapppe.com/os/v2/open-source.svg?v=103" alt="Open Source"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/graphs/contributors"><img src="https://img.shields.io/github/contributors/GouthamSER/KuttuBot?style=flat-square&color=green" alt="Contributors"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL-blue" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python" alt="Python 3.10">
</p>

<p align="center">
  <a href="https://telegram.dog/im_goutham_josh"><img src="https://img.shields.io/badge/Telegram-Support%20Group-30302f?style=flat&logo=telegram" alt="Support Group"></a>
  <a href="https://telegram.dog/wudixh15"><img src="https://img.shields.io/badge/Telegram-Updates%20Channel-30302f?style=flat&logo=telegram" alt="Updates Channel"></a>
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
| File Store with Auto-Delete | ✅ |
| Broadcast to All Users | ✅ |
| Index Channels | ✅ |
| Admin Commands | ✅ |
| Group Connection via PM | ✅ |
| Ban / Unban Users | ✅ |
| User & Chat Stats | ✅ |
| Protect Content | ✅ |
| Auth Channel Subscription Check | ✅ |
| Random Pics on Start | ✅ |

---

## ⚙️ Configuration

Copy `sample_info.py` → `info.py` and fill in your values, **or** set them as environment variables for cloud deployments.

### 🔴 Required Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Get from [@BotFather](https://telegram.dog/BotFather) |
| `API_ID` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `CHANNELS` | Username or ID of channels to index — space-separated |
| `ADMINS` | Username or ID of bot admins — space-separated |
| `DATABASE_URI` | MongoDB connection URI — [get one free](https://www.mongodb.com) |
| `DATABASE_NAME` | Name of your MongoDB database |
| `LOG_CHANNEL` | Channel ID for bot activity logs — bot must be admin there |

### 🟡 Optional Variables

| Variable | Default | Description |
|---|---|---|
| `PICS` | Telegra.ph URLs | Space-separated image links shown on `/start` |
| `FILE_STORE_CHANNEL` | — | Channel IDs for file store links (space-separated) |
| `AUTH_CHANNEL` | — | Force-subscribe channel ID — users must join before getting files |
| `AUTH_USERS` | — | Extra user IDs allowed to use admin features |
| `AUTH_GROUP` | — | Allowed group IDs (space-separated) |
| `CACHE_TIME` | `300` | Inline query cache time in seconds |
| `CUSTOM_FILE_CAPTION` | Script default | Custom caption template for sent files |
| `BATCH_FILE_CAPTION` | Built-in template | Caption used in batch file links |
| `IMDB_TEMPLATE` | Built-in template | Template for IMDB result messages |
| `IMDB` | `False` | Enable IMDB info on search results |
| `LONG_IMDB_DESCRIPTION` | `False` | Show full IMDB plot instead of short summary |
| `SINGLE_BUTTON` | `True` | Show filename + size in one button instead of two |
| `P_TTI_SHOW_OFF` | `True` | Redirect users to bot PM instead of sending file directly in group |
| `SPELL_CHECK_REPLY` | `True` | Suggest similar titles when a file isn't found |
| `MAX_LIST_ELM` | `None` | Limit cast/crew list length in IMDB template |
| `PROTECT_CONTENT` | `False` | Enable forward-protection on sent files |
| `PUBLIC_FILE_STORE` | `False` | Allow anyone to create file store links |
| `MELCOW_NEW_USERS` | `True` | Send a welcome message to new users |
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
# Fill in your variables in info.py or set them as environment vars
docker-compose up -d
```

A `Dockerfile` and `docker-compose.yml` are included in the repo.
</details>

### 🖥️ VPS / Self-Host

<details>
<summary>Click to expand</summary>

```bash
# Requirements: Python 3.10+
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
| `/info` | Get user info |
| `/imdb` | Fetch movie info from IMDB |

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

### 🛡️ Admin Commands

| Command | Description |
|---|---|
| `/logs` | Get recent error logs |
| `/stats` | Get database and file stats |
| `/users` | List all users |
| `/chats` | List all chats |
| `/index` | Index files from a channel |
| `/deleteall` | Delete all indexed files |
| `/delete` | Delete a specific indexed file |
| `/channel` | List all connected channels |
| `/broadcast` | Broadcast a message to all users |
| `/batch` | Create a shareable link for multiple posts |
| `/link` | Create a shareable link for a single post |
| `/leave` | Make the bot leave a chat |
| `/disable` | Disable the bot in a chat |
| `/enable` | Re-enable the bot in a chat |
| `/ban` | Ban a user from the bot |
| `/unban` | Unban a user |
| `/settings` | Configure per-group settings |

---

## 🗂️ Project Structure

```
KuttuBot/
├── bot.py                  # Entry point
├── info.py                 # All configuration variables
├── sample_info.py          # Config template (copy → info.py)
├── utils.py                # Shared utilities
├── Script.py               # All message texts/templates
├── requirements.txt        # Python dependencies
├── plugins/
│   ├── pm_filter.py        # Callback query handler & auto filter
│   ├── filters.py          # Manual filter management
│   ├── broadcast.py        # Broadcast system
│   ├── index.py            # Channel indexing
│   ├── inline.py           # Inline search
│   ├── connection.py       # PM ↔ group connection
│   ├── commands.py         # User-facing commands
│   ├── channel.py          # Channel management
│   ├── misc.py             # Miscellaneous handlers
│   └── ...
└── database/
    ├── ia_filterdb.py      # Indexed file DB
    ├── filters_mdb.py      # Manual filter DB
    └── users_chats_db.py   # Users & chats DB
```

---

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) by **Dan** — the MTProto library powering this bot
- [EvaMaria](https://github.com/ritheshrkrm) by **Mahesh & Ritesh** — original bot base
- [TroJanZ](https://github.com/trojanzhex) — [Unlimited Filter Bot](https://github.com/TroJanzHEX/Unlimited-Filter-Bot) & [AutoFilterBot](https://github.com/trojanzhex/auto-filter-bot)
- [Goutham Josh](https://gouthamjosh.vercel.app) — repo maintainer, bug fixes & improvements
- Everyone who starred, forked, and contributed 💙

---

## ⚠️ Disclaimer

[![GNU AGPL v3](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html)

Licensed under [GNU AGPL v3.0](./LICENSE).

> **Selling this code for money is strictly prohibited.**
> Forking and editing for personal use is welcome — but please credit the original authors and do not rebrand it as your own work. Respect the community that built this. 🙏
