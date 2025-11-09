<p align="center">
  <img src="https://user-images.githubusercontent.com/97418751/212598655-d7637a29-cba8-4ed6-92a4-6534d394b0f7.jpg" alt="ᴋᴜᴛᴛᴜ ʙᴏᴛ™ Logo">
</p>
<h1 align="center">
  <b>ᴋᴜᴛᴛᴜ ʙᴏᴛ™</b>
</h1>


<p align="center">
  A powerful and versatile Telegram bot designed for filtering, automation, and much more!
</p>
<div align="center">
  <a href="https://github.com/GouthamSER/KuttuBot/stargazers">
    <img src="https://img.shields.io/github/stars/GouthamSER/KuttuBot?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Stars" />
  </a>
  <a href="https://github.com/GouthamSER/KuttuBot/network/members">
    <img src="https://img.shields.io/github/forks/GouthamSER/KuttuBot?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Forks" />
  </a>
  <a href="https://github.com/GouthamSER/KuttuBot">
    <img src="https://img.shields.io/github/repo-size/GouthamSER/KuttuBot?color=skyblue&logo=github&logoColor=blue&style=for-the-badge" alt="Repo Size" />
  </a>
  <a href="https://github.com/GouthamSER/KuttuBot/commits/main">
    <img src="https://img.shields.io/github/last-commit/GouthamSER/KuttuBot?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Last Commit" />
  </a>
  <a href="https://github.com/GouthamSER/KuttuBot">
    <img src="https://img.shields.io/github/contributors/GouthamSER/KuttuBot?color=skyblue&logo=github&logoColor=blue&style=for-the-badge" alt="Contributors" />
  </a>
  <a href="https://github.com/GouthamSER/KuttuBot/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-GPL%202.0%20license-blueviolet?style=for-the-badge" alt="License" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Written%20in-Python-skyblue?style=for-the-badge&logo=python" alt="Python" />
  </a>
  <a href="https://pypi.org/project/Pyrogram/">
    <img src="https://img.shields.io/pypi/v/pyrogram?color=white&label=pyrogram&logo=python&logoColor=blue&style=for-the-badge" alt="Pyrogram" />
  </a>
</div>

## ✨ Features

- ✅ Auto Filter and Auto Approval 💥
- ✅️ Restart added with days , hours , minutes check info.py for indexing files help
- ✅ Manual Filter  
- ✅ IMDB Search and Info  
- ✅ Admin Commands  
- ✅ Broadcast Messages  
- ✅ File Indexing
- ✅ User and Chat Stats
- ✅ Auto Delete: Automatically removes user messages after processing, so you don't need a separate auto-delete bot
- ✅ Auto Restart
- ✅ File Storage
- ✅ Keep Alive Function: Prevents the bot from sleeping or shutting down unexpectedly on platforms like Koyeb, eliminating the need for external uptime services like UptimeRobot.
- ✅ Auto delete for files.
- ✅ /movies and /series Commands: Instantly fetch and display the most recently added movies or series with these commands.
- ✅ Multiple Request FSub support: You can add multiple channels. Easily update the required channels with the /fsub command, e.g., /fsub (channel1 id) (channel2 id) (channel3 id).


## Variables

Read [this](https://telegram.dog/Sources_cods) before you start messing up with your edits.

### Required Variables
* `BOT_TOKEN`: Create a bot using [@BotFather](https://telegram.dog/BotFather), and get the Telegram API token.
* `API_ID`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `API_HASH`: Get this value from [telegram.org](https://my.telegram.org/apps)
* `CHANNELS`: Username or ID of channel or group. Separate multiple IDs by space
* `ADMINS`: Username or ID of Admin. Separate multiple Admins by space
* `DATABASE_URI`: [mongoDB](https://www.mongodb.com) URI. Get this value from [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/1G1XwEOnxxo)
* `DATABASE_NAME`: Name of the database in [mongoDB](https://www.mongodb.com). For more help watch this [video](https://youtu.be/Miajl2amrKo)
* `LOG_CHANNEL` : A channel to log the activities of bot. Make sure bot is an admin in the channel.
### Optional Variables
* `PICS`: Telegraph links of images to show in start message.( Multiple images can be used separated by space )
* `FILE_STORE_CHANNEL`: Channel from were file store links of posts should be made.Separate multiple IDs by space
* Check [info.py](https://github.com/8769ANURAG/EvaMaria/blob/master/info.py) for more


## Deploy
You can deploy this bot anywhere.

<details><summary>Deploy To Koyeb</summary>
<p>
<br>
<a href="https://app.koyeb.com/deploy?type=git&repository=github.com/GouthamSER/KuttuBot&env[BOT_TOKEN]&env[API_ID]&env[API_HASH]&env[CHANNELS]&env[ADMINS]&env[PICS]&env[LOG_CHANNEL]&env[AUTH_CHANNEL]&env[CUSTOM_FILE_CAPTION]&env[DATABASE_URI]&env[DATABASE_NAME]&env[COLLECTION_NAME]=Telegram_files&env[FILE_CHANNEL]=-1001832732995&env[SUPPORT_CHAT]&env[IMDB]=True&env[IMDB_TEMPLATE]&env[SINGLE_BUTTON]=True&env[AUTH_GROUPS]&env[P_TTI_SHOW_OFF]=True&branch=main&name=telegrambot">
 <img src="https://www.koyeb.com/static/images/deploy/button.svg">
</a>
</p>
</details>

<details><summary>Deploy To Heroku</summary>
<p>
<br>
<a href="https://heroku.com/deploy?template=https://github.com/GouthamSER/KuttuBot">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">

</a>
</p>
</details>

<details><summary>Deploy To VPS</summary>
<p>
<pre>
git clone https://github.com/GouthamSER/KuttuBot
# Install Packages
pip3 install -U -r requirements.txt
Edit info.py with variables as given below then run bot
python3 bot.py
</pre>
</p>
</details>


## Commands
```
• /logs - to get the rescent errors
• /stats - to get status of files in db.
* /filter - add manual filters
* /filters - view filters
* /connect - connect to PM.
* /disconnect - disconnect from PM
* /del - delete a filter
* /delall - delete all filters
* /deleteall - delete all index(autofilter)
* /delete - delete a specific file from index.
* /info - get user info
* /id - get tg ids.
* /imdb - fetch info from imdb.
• /users - to get list of my users and ids.
• /chats - to get list of the my chats and ids 
• /index  - to add files from a channel
• /leave  - to leave from a chat.
• /disable  -  do disable a chat.
* /enable - re-enable chat.
• /ban  - to ban a user.
• /unban  - to unban a user.
• /channel - to get list of total connected channels
• /broadcast - to broadcast a message to all Eva Maria users
• /batch - to create link for multiple posts
• /link - to create link for one post
```
## Support
[![telegram badge](https://img.shields.io/badge/Telegram-Movie-30302f?style=flat&logo=telegram)](
https://t.me/+53lB8qzQaGFlNDll)




## Thanks to 
 - Thanks To Dan For His Awesome [Library](https://github.com/pyrogram/pyrogram)
 - Thanks To Mahesh For His Goutham [Evamaria](https://github.com/GouthamSER)
 - Thanks To [Trojanz](https://github.com/trojanzhex) for Their Awesome [Unlimited Filter Bot](https://github.com/TroJanzHEX/Unlimited-Filter-Bot) And [AutoFilterBoT](https://github.com/trojanzhex/auto-filter-bot)
 - Thanks To All Everyone In This Journey

### Note

[Note To A So Called Dev](https://telegram.dog/wudixh/13/4/): 

Kanging this codes and and editing a few lines and releasing a V.x  or an [alpha](https://telegram.dog/wudixh/13/4), beta , gama branches of your repo won't make you a Developer.
Fork the repo and edit as per your needs.

## Disclaimer
[![GNU Affero General Public License 2.0](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html#header)    
Licensed under [GNU AGPL 2.0.](https://github.com/GouthamSER/KuttuBot/blob/master/LICENSE)
Selling The Codes To Other People For Money Is *Strictly Prohibited*.
