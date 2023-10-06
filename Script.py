class script(object):
    START_TXT = """👋🏻 Hᴇʟʟᴏ {}.
𝖨𝗆 𝖺𝗇 𝖺𝗎𝗍𝗈 𝖿𝗂𝗅𝗍𝖾𝗋 𝖻𝗈𝗍 𝗐𝗁𝗂𝖼𝗁 𝖼𝖺𝗇 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗆𝗈𝗏𝗂𝖾𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌. 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 𝖺𝗇𝖽 𝗉𝗋𝗈𝗆𝗈𝗍𝖾 𝗆𝖾 𝖺𝗌 𝖺𝖽𝗆𝗂𝗇 𝗍𝗈 𝗅𝖾𝗍 𝗆𝖾 𝗀𝖾𝗍 𝗂𝗇 𝖺𝖼𝗍𝗂𝗈𝗇.
𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖧𝖾𝗅𝗉 𝖻𝗎𝗍𝗍𝗈𝗇 𝖿𝗈𝗋 𝖬𝗈𝗋𝖾...

©️ Maintained By @im_goutham_josh"""
    HELP_TXT = """
    🙋🏻‍♂️   Hellooo  {} 🤓

○ Available Commands
     
 /start - Check I'm Alive..
 /status - Bot Status
 /info - User info 
 /id - User id
 /stats - Db status  
 /broadcast - Broadcast (owner only)

○ Notice 📙:-

○ Dont Spam Me...🙂
"""
    ABOUT_TXT = """<b>◎ Nᴀᴍᴇ: ᴋᴜᴛᴛᴜ ʙᴏᴛ™
◎ Cʀᴇᴀᴛᴏʀ: <a href=https://t.me/wudixh1>Goutham SER</a>
◎ Lᴀɴɢᴜᴀɢᴇ: Pʏᴛʜᴏɴ 3
◎ Dᴀᴛᴀ Bᴀsᴇ: Mᴏɴɢᴏ DB
◎ Bᴏᴛ Sᴇʀᴠᴇʀ: Mogenuis</b>"""
    SOURCE_TXT = """<b>NOTE:</b>
- ᴋᴜᴛᴛᴜ ʙᴏᴛ™ is a open source project. 
- Source - https://github.com/GouthamSER/KuttuBot  

<b>DEVS:</b>
- <a href=https://t.me/wudixh1>ɢᴏᴜᴛʜᴀᴍ sᴇʀ🌈</a>"""
    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Filter is the feature were users can set automated replies for a particular keyword and EvaMaria will respond whenever a keyword is found the message
<b>NOTE:</b>
1. ᴋᴜᴛᴛᴜ ʙᴏᴛ™ should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

- Eva Maria Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Eva Maria supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/sources_cods)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of Eva Maria

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my admins

<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>"""
    STATUS_TXT = """★ 𝚃𝙾𝚃𝙰𝙻 𝙵𝙸𝙻𝙴𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝚄𝚂𝙴𝚁𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂: <code>{}</code>
★ 𝚄𝚂𝙴𝙳 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> 
★ 𝙵𝚁𝙴𝙴 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> """
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
