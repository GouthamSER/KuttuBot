class script(object):
    START_TXT = """👋🏻 Hᴇʟʟᴏ {},
𝖨𝗆 𝖺𝗇 𝖺𝗎𝗍𝗈 𝖿𝗂𝗅𝗍𝖾𝗋 𝖻𝗈𝗍 𝗐𝗁𝗂𝖼𝗁 𝖼𝖺𝗇 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝗆𝗈𝗏𝗂𝖾𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉𝗌. 𝖠𝖽𝖽 𝖬𝖾 𝖳𝗈 𝖸𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 𝖺𝗇𝖽 𝗉𝗋𝗈𝗆𝗈𝗍𝖾 𝗆𝖾 𝖺𝗌 𝖺𝖽𝗆𝗂𝗇 𝗍𝗈 𝗅𝖾𝗍 𝗆𝖾 𝗀𝖾𝗍 𝗂𝗇 𝖺𝖼𝗍𝗂𝗈𝗇.
𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖧𝖾𝗅𝗉 𝖻𝗎𝗍𝗍𝗈𝗇 𝖿𝗈𝗋 𝖬𝗈𝗋𝖾...

⚡️ Maintained By @im_goutham_josh"""

    HELP_TXT = """
🙋🏻‍♂️  𝗪𝗲𝗹𝗰𝗼𝗺𝗲, {}! 🎉

📋 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀
━━━━━━━━━━━━━━━━━━━

 /start   » 𝘊𝘩𝘦𝘤𝘬 𝘐'𝘮 𝘈𝘭𝘪𝘷𝘦
 /status  » 𝘉𝘰𝘵 𝘚𝘵𝘢𝘵𝘶𝘴
 /info    » 𝘜𝘴𝘦𝘳 𝘐𝘯𝘧𝘰
 /id      » 𝘜𝘴𝘦𝘳 𝘐𝘋
 /stats   » 𝘋𝘣 𝘚𝘵𝘢𝘵𝘶𝘴
 /broadcast » 𝘉𝘳𝘰𝘢𝘥𝘤𝘢𝘴𝘵 (𝘖𝘸𝘯𝘦𝘳 𝘖𝘯𝘭𝘺)

⚠️ 𝗡𝗼𝘁𝗶𝗰𝗲:
🔇 𝘋𝘰𝘯'𝘵 𝘚𝘱𝘢𝘮 𝘔𝘦... 😅
"""

    ABOUT_TXT = """<b>🔷 Nᴀᴍᴇ : ᴋᴜᴛᴛᴜ ʙᴏᴛ™
🔷 Cʀᴇᴀᴛᴏʀ : <a href=https://t.me/wudixh13>Goutham SER</a>
🔷 Lᴀɴɢᴜᴀɢᴇ : Pʏᴛʜᴏɴ 3
🔷 Dᴀᴛᴀʙᴀsᴇ : Mᴏɴɢᴏ DB
🔷 Sᴇʀᴠᴇʀ : KoYeb</b>"""

    SOURCE_TXT = """<b>📌 NOTE:</b>
• ᴋᴜᴛᴛᴜ ʙᴏᴛ™ is an open source project.
• Source → <a href=https://github.com/GouthamSER>𝘊𝘭𝘪𝘤𝘬 𝘏𝘦𝘳𝘦 🚀</a>

<b>👨‍💻 DEVS:</b>
• <a href=https://t.me/wudixh1>𝔊𝔬𝔲𝔱𝔥𝔞𝔪 𝔖𝔢𝔯 ⚠️</a>"""

    MANUELFILTER_TXT = """🔧 Help: <b>Filters</b>
━━━━━━━━━━━━━━━━━━━
𝘍𝘪𝘭𝘵𝘦𝘳𝘴 𝘢𝘭𝘭𝘰𝘸 𝘢𝘶𝘵𝘰𝘮𝘢𝘵𝘦𝘥 𝘳𝘦𝘱𝘭𝘪𝘦𝘴 𝘧𝘰𝘳 𝘴𝘱𝘦𝘤𝘪𝘧𝘪𝘤 𝘬𝘦𝘺𝘸𝘰𝘳𝘥𝘴.

<b>⚠️ NOTE:</b>
1️⃣ Bot must have admin privileges.
2️⃣ Only admins can add filters.
3️⃣ Alert buttons have a 64-character limit.

<b>📌 Commands & Usage:</b>
• /filter   — <code>add a filter in chat</code>
• /filters  — <code>list all filters of a chat</code>
• /del      — <code>delete a specific filter</code>
• /delall   — <code>delete all filters (owner only)</code>"""

    BUTTON_TXT = """🔘 Help: <b>Buttons</b>
━━━━━━━━━━━━━━━━━━━
𝘚𝘶𝘱𝘱𝘰𝘳𝘵𝘴 𝘣𝘰𝘵𝘩 𝘜𝘙𝘓 𝘢𝘯𝘥 𝘈𝘭𝘦𝘳𝘵 𝘪𝘯𝘭𝘪𝘯𝘦 𝘣𝘶𝘵𝘵𝘰𝘯𝘴.

<b>⚠️ NOTE:</b>
1️⃣ Content is mandatory with buttons.
2️⃣ Supports all Telegram media types.
3️⃣ Use proper Markdown formatting.

<b>🔗 URL Buttons:</b>
<code>[Button Text](buttonurl:https://t.me/sources_cods)</code>

<b>🔔 Alert Buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""

    AUTOFILTER_TXT = """🎬 Help: <b>Auto Filter</b>
━━━━━━━━━━━━━━━━━━━

<b>⚠️ NOTE:</b>
1️⃣ Make me admin of your channel if it's private.
2️⃣ No camrips, adult content or fake files.
3️⃣ Forward the last message to me with quotes.
    ✅ I'll index all files from that channel into my DB."""

    CONNECTION_TXT = """🔗 Help: <b>Connections</b>
━━━━━━━━━━━━━━━━━━━
𝘊𝘰𝘯𝘯𝘦𝘤𝘵 𝘣𝘰𝘵 𝘵𝘰 𝘗𝘔 𝘵𝘰 𝘮𝘢𝘯𝘢𝘨𝘦 𝘧𝘪𝘭𝘵𝘦𝘳𝘴 & 𝘢𝘷𝘰𝘪𝘥 𝘨𝘳𝘰𝘶𝘱 𝘴𝘱𝘢𝘮.

<b>⚠️ NOTE:</b>
1️⃣ Only admins can add a connection.
2️⃣ Send <code>/connect</code> to connect via PM.

<b>📌 Commands & Usage:</b>
• /connect     — <code>connect a chat to your PM</code>
• /disconnect  — <code>disconnect from a chat</code>
• /connections — <code>list all your connections</code>"""

    EXTRAMOD_TXT = """🧩 Help: <b>Extra Modules</b>
━━━━━━━━━━━━━━━━━━━

<b>📌 Commands & Usage:</b>
• /id     — <code>get ID of a user</code>
• /info   — <code>get information about a user</code>
• /imdb   — <code>get film info from IMDb</code>
• /search — <code>get film info from various sources</code>"""

    ADMIN_TXT = """🛡️ Help: <b>Admin Modules</b>
━━━━━━━━━━━━━━━━━━━
⚠️ <i>This module is for bot admins only.</i>

<b>📌 Commands & Usage:</b>
• /logs      — <code>get recent errors</code>
• /stats     — <code>file count in DB</code>
• /delete    — <code>delete a specific file from DB</code>
• /users     — <code>list users and IDs</code>
• /chats     — <code>list chats and IDs</code>
• /leave     — <code>leave from a chat</code>
• /disable   — <code>disable a chat</code>
• /ban       — <code>ban a user</code>
• /unban     — <code>unban a user</code>
• /channel   — <code>list connected channels</code>
• /broadcast — <code>broadcast a message to all users</code>"""

    STATUS_TXT = """╔══════════════════════╗
   📊  𝗕𝗢𝗧  𝗦𝗧𝗔𝗧𝗨𝗦
╚══════════════════════╝
🎞️ 𝚃𝙾𝚃𝙰𝙻 𝙵𝙸𝙻𝙴𝚂  : <code>{}</code>
👥 𝚃𝙾𝚃𝙰𝙻 𝚄𝚂𝙴𝚁𝚂  : <code>{}</code>
💬 𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂  : <code>{}</code>
🗄️ 𝚄𝚂𝙴𝙳 𝚂𝚃𝙾𝚁𝙰𝙶𝙴 : <code>{}</code>
💾 𝙵𝚁𝙴𝙴 𝚂𝚃𝙾𝚁𝙰𝙶𝙴 : <code>{}</code>"""

    LOG_TEXT_G = """#️⃣ #NewGroup
🏘️ Group  = {}(<code>{}</code>)
👥 Members = <code>{}</code>
➕ Added By = {}
"""

    RESULT_TXT = """✅ 𝓗𝓮𝔂 {}! 𝓘 𝓕𝓸𝓾𝓷𝓭 𝓘𝓽 𝓘𝓷 𝓜𝔂 𝓓𝓪𝓽𝓪𝓫𝓪𝓼𝓮 🎯"""

    CUSTOM_FILE_CAPTION = """<b>📁 Fɪʟᴇɴᴀᴍᴇ  : {file_name}
📦 Fɪʟᴇ Sɪᴢᴇ : {file_size}

╔══ 🌐 ᴊᴏɪɴ ᴡɪᴛʜ ᴜs ══╗
✨ <a href=https://t.me/+53lB8qzQaGFlNDll> ᴇʟᴅᴏʀᴀᴅᴏ </a>
╚══ 🌐 ᴊᴏɪɴ ᴡɪᴛʜ ᴜs ══╝</b>"""

    RESTART_TXT = """
<b>🔄 Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ ✅
⚡️ @im_goutham_josh</b>"""

    LOG_TEXT_P = """#️⃣ #NewUser
🆔 ID   — <code>{}</code>
👤 Name — {}
"""

    SPOLL_NOT_FND = """😔 𝓞𝓸𝓹𝓼! 𝓝𝓸𝓽𝓱𝓲𝓷𝓰 𝓕𝓸𝓾𝓷𝓭 🤷‍♂️
I couldn't find anything related to your request.
👇🏼 𝘛𝘳𝘺 𝘳𝘦𝘢𝘥𝘪𝘯𝘨 𝘵𝘩𝘦 𝘪𝘯𝘴𝘵𝘳𝘶𝘤𝘵𝘪𝘰𝘯𝘴 𝘣𝘦𝘭𝘰𝘸 👇🏼
    """

    ENG_SPELL = """📖 𝗣𝗹𝗲𝗮𝘀𝗲 𝗡𝗼𝘁𝗲:
1️⃣ Ask with correct spelling
2️⃣ Don't ask for movies not released on OTT platforms
3️⃣ Try: [movie name language] or [movie name year]
    """

    MAL_SPELL = """📖 ദയവായി ശ്രദ്ധിക്കുക:
1️⃣ ശരിയായ അക്ഷരവിന്യാസത്തിൽ ചോദിക്കുക
2️⃣ OTT പ്ലാറ്റ്‌ഫോമുകളിൽ റിലീസ് ചെയ്യാത്ത സിനിമകൾ ചോദിക്കരുത്
3️⃣ ഇത് പോലെ [സിനിമയുടെ പേര് ഭാഷ] അല്ലെങ്കിൽ [സിനിമ വർഷം] ചോദിക്കാം
    """

    HIN_SPELL = """📖 कृपया ध्यान दें:
1️⃣ सही वर्तनी में पूछें
2️⃣ OTT पर रिलीज़ न हुई फ़िल्में न पूछें
3️⃣ इस तरह पूछें: [फ़िल्म का नाम भाषा] या [फ़िल्म वर्ष]
    """

    TAM_SPELL = """📖 கவனிக்கவும்:
1️⃣ சரியான எழுத்துப்பிழையில் கேளுங்கள்
2️⃣ OTT-இல் வெளியாகாத திரைப்படங்களைக் கேட்காதீர்கள்
3️⃣ இந்த வடிவத்தில் கேளுங்கள்: [திரைப்படத்தின் பெயர், ஆண்டு]
    """

    CHK_MOV_ALRT = """🔍 𝓢𝓮𝓪𝓻𝓬𝓱𝓲𝓷𝓰 𝓨𝓸𝓾𝓻 𝓕𝓲𝓵𝓮 𝓘𝓷 𝓜𝔂 𝓓𝓪𝓽𝓪𝓫𝓪𝓼𝓮... ⏳"""

    OLD_MES = """⚠️ 𝘠𝘰𝘶 𝘢𝘳𝘦 𝘶𝘴𝘪𝘯𝘨 𝘰𝘯𝘦 𝘰𝘧 𝘮𝘺 𝘰𝘭𝘥 𝘮𝘦𝘴𝘴𝘢𝘨𝘦𝘴 🕰️
🔁 𝘗𝘭𝘦𝘢𝘴𝘦 𝘴𝘦𝘯𝘥 𝘺𝘰𝘶𝘳 𝘳𝘦𝘲𝘶𝘦𝘴𝘵 𝘢𝘨𝘢𝘪𝘯."""

    MOV_NT_FND = """<b>❌ 𝓣𝓱𝓲𝓼 𝓜𝓸𝓿𝓲𝓮 𝓘𝓼 𝓝𝓸𝓽 𝓨𝓮𝓽 𝓡𝓮𝓵𝓮𝓪𝓼𝓮𝓭 𝓸𝓻 𝓐𝓭𝓭𝓮𝓭 𝓣𝓸 𝓓𝓑 🎬</b>
📩 Report To Admin — @im_goutham_josh
"""

    DMCA_TXT = """<b><u>⚖️ DMCA Compliance Notice</u></b>

<blockquote>🛡️ This Telegram bot operates within the guidelines of the Digital Millennium Copyright Act (DMCA) and fully respects intellectual property rights. We respond promptly to all valid DMCA takedown notices.</blockquote>

📧 <b>Send your DMCA takedown notice to:</b>
<code>dmcarexie@proton.me</code>
"""
