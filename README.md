<p align="center">
  <img src="https://user-images.githubusercontent.com/97418751/212598655-d7637a29-cba8-4ed6-92a4-6534d394b0f7.jpg" alt="ᴋᴜᴛᴛᴜ ʙᴏᴛ™ Logo" width="200">
</p>

<h1 align="center">ᴋᴜᴛᴛᴜ ʙᴏᴛ™</h1>

<p align="center">
  <a href="https://github.com/GouthamSER/KuttuBot/stargazers"><img src="https://img.shields.io/github/stars/GouthamSER/KuttuBot?style=flat-square&color=yellow" alt="Stars"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/fork"><img src="https://img.shields.io/github/forks/GouthamSER/KuttuBot?style=flat-square&color=orange" alt="Forks"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/"><img src="https://img.shields.io/github/repo-size/GouthamSER/KuttuBot?style=flat-square&color=green" alt="Size"></a>
  <a href="https://github.com/GouthamSER/KuttuBot"><img src="https://badges.frapsoft.com/os/v2/open-source.svg?v=103" alt="Open Source"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/graphs/contributors"><img src="https://img.shields.io/github/contributors/GouthamSER/KuttuBot?style=flat-square&color=green" alt="Contributors"></a>
  <a href="https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-AGPL-blue" alt="License"></a>
</p>

<p align="center">
  <a href="https://telegram.dog/Technical_Help_Support_Bot"><img src="https://img.shields.io/badge/Telegram-Support%20Group-30302f?style=flat&logo=telegram" alt="Support Group"></a>
  <a href="https://telegram.dog/sources_cods"><img src="https://img.shields.io/badge/Telegram-Updates%20Channel-30302f?style=flat&logo=telegram" alt="Updates Channel"></a>
</p>

---

## ✨ Features

| Feature | Status |
|---|---|
| Auto Filter | ✅ |
| Manual Filter | ✅ |
| IMDB Info & Search | ✅ |
| Inline Search | ✅ |
| Spelling Check | ✅ |
| File Store | ✅ |
| Broadcast | ✅ |
| Index Channels | ✅ |
| Admin Commands | ✅ |
| Random Pics | ✅ |
| User & Chat Stats | ✅ |
| Ban / Unban Users | ✅ |

---

## ⚙️ Variables

> Read [this](https://telegram.dog/Sources_cods) before editing your config.

### 🔴 Required

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Create a bot via [@BotFather](https://telegram.dog/BotFather) and get the token |
| `API_ID` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Get from [my.telegram.org](https://my.telegram.org/apps) |
| `CHANNELS` | Username or ID of channels/groups — separate multiple by space |
| `ADMINS` | Username or ID of admins — separate multiple by space |
| `DATABASE_URI` | MongoDB URI — [get from MongoDB](https://www.mongodb.com) · [video guide](https://youtu.be/1G1XwEOnxxo) |
| `DATABASE_NAME` | Name of your MongoDB database · [video guide](https://youtu.be/Miajl2amrKo) |
| `LOG_CHANNEL` | Channel to log bot activity — bot must be admin there |

### 🟡 Optional

| Variable | Description |
|---|---|
| `PICS` | Telegraph image links for start message (multiple, space-separated) |
| `FILE_STORE_CHANNEL` | Channel for file store links (multiple IDs, space-separated) |

> See [info.py](https://github.com/GouthamSER/KuttuBot/blob/master/info.py) for all available variables.

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

### 🖥️ VPS / Self-Host

<details>
<summary>Click to expand</summary>

```bash
git clone https://github.com/GouthamSER/KuttuBot
cd KuttuBot
pip3 install -U -r requirements.txt
# Edit info.py with your variables
python3 bot.py
```
</details>

---

## 📋 Commands

### 👤 User Commands
```
/start      - Start the bot
/help       - Get help info
/about      - About the bot
/id         - Get Telegram IDs
/info       - Get user info
/imdb       - Fetch info from IMDB
```

### 🔧 Filter Commands
```
/filter     - Add a manual filter
/filters    - View all filters
/del        - Delete a filter
/delall     - Delete all filters
/connect    - Connect to PM
/disconnect - Disconnect from PM
```

### 🛡️ Admin Commands
```
/logs       - Get recent error logs
/stats      - Get database file stats
/users      - List all users and IDs
/chats      - List all chats and IDs
/index      - Index files from a channel
/deleteall  - Delete all indexed files
/delete     - Delete a specific indexed file
/channel    - List all connected channels
/broadcast  - Broadcast a message to all users
/batch      - Create a link for multiple posts
/link       - Create a link for a single post
/leave      - Leave a chat
/disable    - Disable a chat
/enable     - Re-enable a chat
/ban        - Ban a user
/unban      - Unban a user
```

---

## 🙏 Credits

- [Pyrogram](https://github.com/pyrogram/pyrogram) by **Dan** — the awesome MTProto library
- [EvaMaria](https://github.com/ritheshrkrm) by **Mahesh & Ritesh** — original bot base
- [TroJanZ](https://github.com/trojanzhex) — [Unlimited Filter Bot](https://github.com/TroJanzHEX/Unlimited-Filter-Bot) & [AutoFilterBot](https://github.com/trojanzhex/auto-filter-bot)
- Everyone who supported this project along the way 💙
- [Goutham SER](https://gouthamjosh.vercel.app) by **Goutham Josh** — Repo Redited with BUGFREE

---

## ⚠️ Disclaimer

[![GNU AGPL v3](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html)

Licensed under [GNU AGPL v3.0](https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE).

> **Selling this code for money is strictly prohibited.**
> Forking and editing for personal use is welcome — but simply copying a few lines and releasing it as your own "v2.0 alpha" does not make you a developer. Please respect the original work. 🙏
