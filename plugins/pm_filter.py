# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
from urllib.parse import quote_plus
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, QueryIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FRESH = {}

# ── Filter lists ───────────────────────────────────────────────────────────────
YEARS = [str(y) for y in range(2025, 1999, -1)]

# Language: display label → search keyword
LANGUAGES = [
    ("MAL", "malayalam"),
    ("TAM", "tamil"),
    ("KAN", "kannada"),
    ("ENG", "english"),
    ("TEL", "telugu"),
    ("HIN", "hindi"),
    ("PUN", "punjabi"),
    ("BEN", "bengali"),
    ("MAR", "marathi"),
    ("GUJ", "gujarati"),
    ("URD", "urdu"),
    ("KOR", "korean"),
    ("JAP", "japanese"),
    ("CHN", "chinese"),
    ("FRE", "french"),
    ("SPA", "spanish"),
    ("ARB", "arabic"),
    ("RUS", "russian"),
]

# Seasons: display label → search keyword (s01 format)
SEASONS = [(f"S{str(i).zfill(2)}", f"s{str(i).zfill(2)}") for i in range(1, 11)]

# Episodes: display label → search keyword (e01 format)
EPISODES = [(f"E{str(i).zfill(2)}", f"e{str(i).zfill(2)}") for i in range(1, 26)]

QUALITIES = [
    "4K", "1080p", "720p", "480p", "360p", "BluRay",
    "WEB-DL", "HDRip", "DVDRip", "HDTV", "CAMRip", "HDCam"
]
if len(QUALITIES) % 2 != 0:
    QUALITIES.append("Other")


# ── Helper: never crash on expired / already-answered queries ──────────────────
async def safe_answer(query, *args, **kwargs):
    try:
        await query.answer(*args, **kwargs)
    except QueryIdInvalid:
        pass


# ── Helper: build the standard filter-row buttons ─────────────────────────────
def _filter_rows(key):
    return [
        [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥",   callback_data=f"sendfiles#{key}"),
            InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
            InlineKeyboardButton("ʏᴇᴀʀs",      callback_data=f"years#{key}"),
        ],
        [
            InlineKeyboardButton("ǫᴜᴀʟɪᴛʏ",  callback_data=f"qualities#{key}"),
            InlineKeyboardButton("ᴇᴘɪsᴏᴅᴇs", callback_data=f"episodes#{key}"),
            InlineKeyboardButton("sᴇᴀsᴏɴs",  callback_data=f"seasons#{key}"),
        ],
    ]


# ── Helper: rebuild file-list buttons after a filter ──────────────────────────
def _build_file_btn(files, settings, pre, key, offset, total_results, req):
    if settings["button"]:
        btn = [
            [InlineKeyboardButton(
                text=f"📁[{get_size(file.file_size)}]-🎭-{file.file_name}",
                callback_data=f"{pre}#{file.file_id}"
            )]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}",          callback_data=f"{pre}#{file.file_id}"),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f"{pre}#{file.file_id}"),
            ]
            for file in files
        ]

    # prepend filter rows
    for row in reversed(_filter_rows(key)):
        btn.insert(0, row)

    # pagination
    if offset not in ("", 0, None):
        btn.append([
            InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results)/10)}", callback_data="pages"),
            InlineKeyboardButton(text="NEXT ▶️", callback_data=f"next_{req}_{key}_{offset}"),
        ])
    else:
        btn.append([InlineKeyboardButton(text="📃 1/1", callback_data="pages")])

    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  MESSAGE HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)


# ══════════════════════════════════════════════════════════════════════════════
#  NEXT-PAGE HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await safe_answer(query, "**Search for Yourself**🔎", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0

    search = FRESH.get(key) or BUTTONS.get(key)
    if not search:
        await safe_answer(query, script.OLD_MES, show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'

    if settings['button']:
        btn = [
            [InlineKeyboardButton(
                text=f"📁[{get_size(file.file_size)}]-🎭-{file.file_name}",
                callback_data=f'files#{file.file_id}'
            )]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}",          callback_data=f'files#{file.file_id}'),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f'files_#{file.file_id}'),
            ]
            for file in files
        ]

    for row in reversed(_filter_rows(key)):
        btn.insert(0, row)

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10

    if n_offset == 0:
        btn.append([
            InlineKeyboardButton("◀️ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
            InlineKeyboardButton(f"📃 {math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
        ])
    elif off_set is None:
        btn.append([
            InlineKeyboardButton(f"📃 {math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
            InlineKeyboardButton("NEXT ▶️", callback_data=f"next_{req}_{key}_{n_offset}"),
        ])
    else:
        btn.append([
            InlineKeyboardButton("◀️ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
            InlineKeyboardButton(f"📃 {math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
            InlineKeyboardButton("NEXT ▶️", callback_data=f"next_{req}_{key}_{n_offset}"),
        ])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


# ══════════════════════════════════════════════════════════════════════════════
#  SPELL-CHECK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await safe_answer(query, "Search for Yourself🔎", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await safe_answer(query, script.OLD_MES, show_alert=True)
    movie = movies[(int(movie_))]
    await safe_answer(query, script.CHK_MOV_ALRT)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(script.MOV_NT_FND)
            await asyncio.sleep(10)
            await k.delete()


# ══════════════════════════════════════════════════════════════════════════════
#  YEARS FILTER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(YEARS) - 1, 4):
        row = []
        for j in range(4):
            if i + j < len(YEARS):
                row.append(InlineKeyboardButton(
                    text=YEARS[i + j],
                    callback_data=f"fy#{YEARS[i + j]}#{key}"
                ))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton("📅 Sᴇʟᴇᴄᴛ Yᴇᴀʀ", callback_data="pages")])
    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


@Client.on_callback_query(filters.regex(r"^fy#"))
async def filter_years_cb_handler(client: Client, query: CallbackQuery):
    _, year, key = query.data.split("#")
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    base_search = FRESH.get(key)
    if not base_search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    search = f"{base_search} {year}" if year != "homepage" else base_search
    BUTTONS[key] = search

    req = query.from_user.id
    chat_id = query.message.chat.id
    files, offset, total_results = await get_search_results(search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 No Files Found 🚫", show_alert=True)

    settings = await get_settings(chat_id)
    pre = 'filep' if settings['file_secure'] else 'file'
    btn = _build_file_btn(files, settings, pre, key, offset, total_results, req)

    if year != "homepage":
        btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


# ══════════════════════════════════════════════════════════════════════════════
#  EPISODES FILTER  (e01, e02, e03 ... format)
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    _, key = query.data.split("#")
    btn = []
    # 5 episode buttons per row
    for i in range(0, len(EPISODES), 5):
        row = []
        for label, value in EPISODES[i:i+5]:
            row.append(InlineKeyboardButton(
                text=label,
                callback_data=f"fe#{value}#{key}"
            ))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton("🎬 Sᴇʟᴇᴄᴛ Eᴘɪsᴏᴅᴇ", callback_data="pages")])
    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: CallbackQuery):
    _, ep, key = query.data.split("#")
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    base_search = FRESH.get(key)
    if not base_search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    if ep == "homepage":
        search = base_search
    else:
        # e01 → also try "episode 01" and "episode 1" variants for broader matching
        ep_num = ep[1:]  # strip leading 'e'
        ep_num_stripped = str(int(ep_num))  # remove leading zero for "episode 1" style
        search = f"{base_search} {ep}"

    BUTTONS[key] = search

    req = query.from_user.id
    chat_id = query.message.chat.id

    all_files = []
    seen_ids = set()

    if ep != "homepage":
        search_variants = [
            f"{base_search} {ep}",                          # e01
            f"{base_search} episode {ep_num}",              # episode 01
            f"{base_search} episode {ep_num_stripped}",     # episode 1
        ]
        for sq in search_variants:
            f_list, _, _ = await get_search_results(sq, offset=0, filter=True)
            for f in f_list:
                if f.file_id not in seen_ids:
                    seen_ids.add(f.file_id)
                    all_files.append(f)
    else:
        all_files, offset, total_results = await get_search_results(base_search, offset=0, filter=True)

    if not all_files:
        return await query.answer("🚫 No Files Found 🚫", show_alert=True)

    settings = await get_settings(chat_id)
    pre = 'filep' if settings['file_secure'] else 'file'

    # Use fake offset/total for _build_file_btn when deduplicating manually
    offset = ""
    total_results = len(all_files)
    btn = _build_file_btn(all_files, settings, pre, key, offset, total_results, req)

    if ep != "homepage":
        btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fe#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


# ══════════════════════════════════════════════════════════════════════════════
#  LANGUAGES FILTER  (MAL, TAM, KAN, ENG, TEL ... format)
#  → After selecting a language, results are shown immediately (no extra back button needed)
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    _, key = query.data.split("#")
    btn = []
    # 3 language buttons per row
    for i in range(0, len(LANGUAGES), 3):
        row = []
        for label, value in LANGUAGES[i:i+3]:
            row.append(InlineKeyboardButton(
                text=label,
                callback_data=f"fl#{value}#{key}"
            ))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton("🌐 Sᴇʟᴇᴄᴛ Lᴀɴɢᴜᴀɢᴇ", callback_data="pages")])
    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fl#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    base_search = FRESH.get(key)
    if not base_search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    search = f"{base_search} {lang}" if lang != "homepage" else base_search
    BUTTONS[key] = search

    req = query.from_user.id
    chat_id = query.message.chat.id
    files, offset, total_results = await get_search_results(search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 No Files Found 🚫", show_alert=True)

    settings = await get_settings(chat_id)
    pre = 'filep' if settings['file_secure'] else 'file'

    # Build result buttons — filter rows already included via _build_file_btn
    # No extra "Back to Home" button; the filter row's language button lets them re-pick
    btn = _build_file_btn(files, settings, pre, key, offset, total_results, req)

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    # Auto-answer with a toast showing which language was selected
    display_label = lang.upper() if lang != "homepage" else "Home"
    await safe_answer(query, f"✅ {display_label} results loaded!", show_alert=False)


# ══════════════════════════════════════════════════════════════════════════════
#  SEASONS FILTER  (S01, S02, S03 ... format)
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    _, key = query.data.split("#")
    btn = []
    # 5 season buttons per row
    for i in range(0, len(SEASONS), 5):
        row = []
        for label, value in SEASONS[i:i+5]:
            row.append(InlineKeyboardButton(
                text=label,
                callback_data=f"fs#{value}#{key}"
            ))
        btn.append(row)

    btn.insert(0, [InlineKeyboardButton("🎞️ Sᴇʟᴇᴄᴛ Sᴇᴀsᴏɴ", callback_data="pages")])
    req = query.from_user.id
    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_0")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    base_search = FRESH.get(key)
    if not base_search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    req = query.from_user.id
    chat_id = query.message.chat.id
    all_files = []
    seen_ids = set()

    if seas != "homepage":
        # seas = "s01", "s02", etc.
        num = seas[1:]                      # "01"
        num_stripped = str(int(num))        # "1"

        # Search variants: s01 / season 01 / season 1
        search_variants = [
            f"{base_search} {seas}",                     # s01
            f"{base_search} season {num}",               # season 01
            f"{base_search} season {num_stripped}",      # season 1
        ]
        for sq in search_variants:
            f_list, _, _ = await get_search_results(sq, offset=0, filter=True)
            for f in f_list:
                if f.file_id not in seen_ids:
                    seen_ids.add(f.file_id)
                    all_files.append(f)
    else:
        all_files, _, _ = await get_search_results(base_search, offset=0, filter=True)

    if not all_files:
        return await query.answer("🚫 No Files Found 🚫", show_alert=True)

    settings = await get_settings(chat_id)
    pre = 'filep' if settings['file_secure'] else 'file'

    if settings["button"]:
        btn = [
            [InlineKeyboardButton(
                text=f"📁[{get_size(f.file_size)}]-🎭-{f.file_name}",
                callback_data=f"{pre}#{f.file_id}"
            )]
            for f in all_files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f.file_name,           callback_data=f"{pre}#{f.file_id}"),
                InlineKeyboardButton(text=get_size(f.file_size), callback_data=f"{pre}#{f.file_id}"),
            ]
            for f in all_files
        ]

    for row in reversed(_filter_rows(key)):
        btn.insert(0, row)

    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{req}_{key}_0")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


# ══════════════════════════════════════════════════════════════════════════════
#  QUALITIES FILTER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(QUALITIES) - 1, 2):
        btn.append([
            InlineKeyboardButton(text=QUALITIES[i],     callback_data=f"fq#{QUALITIES[i].lower()}#{key}"),
            InlineKeyboardButton(text=QUALITIES[i + 1], callback_data=f"fq#{QUALITIES[i + 1].lower()}#{key}"),
        ])

    btn.insert(0, [InlineKeyboardButton("🎥 Sᴇʟᴇᴄᴛ Qᴜᴀʟɪᴛʏ", callback_data="pages")])
    btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fq#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("⚠️ This is not your request!", show_alert=True)
    except:
        pass

    base_search = FRESH.get(key)
    if not base_search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    search = f"{base_search} {qual}" if qual != "homepage" else base_search
    BUTTONS[key] = search

    req = query.from_user.id
    chat_id = query.message.chat.id
    files, offset, total_results = await get_search_results(search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 No Files Found 🚫", show_alert=True)

    settings = await get_settings(chat_id)
    pre = 'filep' if settings['file_secure'] else 'file'
    btn = _build_file_btn(files, settings, pre, key, offset, total_results, req)

    if qual != "homepage":
        btn.append([InlineKeyboardButton("↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fq#homepage#{key}")])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await safe_answer(query)


# ══════════════════════════════════════════════════════════════════════════════
#  SEND-ALL HANDLER  (files auto-deleted from PM after 5 minutes)
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query(filters.regex(r"^sendfiles#"))
async def send_all_files(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    search = FRESH.get(key) or BUTTONS.get(key)
    if not search:
        return await safe_answer(query, script.OLD_MES, show_alert=True)

    files, _, _ = await get_search_results(search, offset=0, filter=True)
    if not files:
        return await safe_answer(query, "No files to send!", show_alert=True)

    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'

    sent_msgs = []
    for file in files:
        try:
            m = await client.send_cached_media(
                chat_id=query.from_user.id,
                file_id=file.file_id,
                protect_content=(pre == 'filep')
            )
            sent_msgs.append(m)
        except UserIsBlocked:
            return await safe_answer(query, "Unblock the bot first!", show_alert=True)
        except Exception:
            pass

    if not sent_msgs:
        return

    # Send warning notice
    notice = await client.send_message(
        chat_id=query.from_user.id,
        text=(
            "<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n"
            f"📦 <b>{len(sent_msgs)} file(s)</b> sent to your PM!\n\n"
            "⏳ Files will be <b>deleted in 5 minutes</b>\n\n"
            "📌 Save or forward them before they disappear!</blockquote>"
        )
    )

    await safe_answer(query, f"✅ {len(sent_msgs)} file(s) sent! Auto-delete in 5 min.", show_alert=True)

    # Wait 5 minutes then delete all sent files + notice
    await asyncio.sleep(300)

    for m in sent_msgs:
        try:
            await m.delete()
        except Exception:
            pass

    try:
        await notice.edit_text("<b>✅ Files ʜᴀᴠᴇ ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʏᴏᴜʀ PM</b>")
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  GENERAL CALLBACK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await safe_answer(query, 'Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await safe_answer(query, 'Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await safe_answer(query, 'Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await safe_answer(query, "You need to be Group Owner or an Auth User to do that!", show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await safe_answer(query, "That's not for you!!", show_alert=True)

    elif "groupcb" in query.data:
        group_id = query.data.split(":")[1]
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif "connectcb" in query.data:
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await safe_answer(query, 'Piracy Is Crime')

    elif "disconnect" in query.data:
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await safe_answer(query, 'Piracy Is Crime')

    elif "deletecb" in query.data:
        user_id = query.from_user.id
        group_id = query.data.split(":")[1]
        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text("Successfully deleted connection")
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "backcb":
        userid = query.from_user.id
        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await safe_answer(query, 'Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append([
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ])
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return await safe_answer(query, 'Piracy Is Crime')

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await safe_answer(query, alert, show_alert=True)
        return

    # ── File handler ──────────────────────────────────────────────────────────
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await safe_answer(query, 'No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await safe_answer(query, url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await safe_answer(query, url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False
                )
                await safe_answer(query, '**Already Sent In your Pm**', show_alert=True)
        except UserIsBlocked:
            await safe_answer(query, 'Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await safe_answer(query, url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await safe_answer(query, url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        return

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await safe_answer(query, "I Like Your Smartness, But Don't Be Oversmart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await safe_answer(query, 'No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await safe_answer(query)
        m = await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
        k = await client.send_message(
            chat_id=query.from_user.id,
            text=(
                "<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n"
                "⚠️ File will be deleted in 10 Mins\n\n"
                "📌 Save or forward it.</blockquote>"
            )
        )
        await asyncio.sleep(600)
        await m.delete()
        await k.edit_text("<b>✅ Yᴏᴜʀ File ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ</b>")
        return

    elif query.data == "pages":
        await safe_answer(query)
        return

    elif query.data == "esp":
        await safe_answer(query, text=script.ENG_SPELL, show_alert=True)
        return

    elif query.data == "msp":
        await safe_answer(query, text=script.MAL_SPELL, show_alert=True)
        return

    elif query.data == "hsp":
        await safe_answer(query, text=script.HIN_SPELL, show_alert=True)
        return

    elif query.data == "tsp":
        await safe_answer(query, text=script.TAM_SPELL, show_alert=True)
        return

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('🎉 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀 🎉', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🛠️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('🛡️ ᴀʙᴏᴜᴛ', callback_data='about')
        ], [
            InlineKeyboardButton('✔ DMCA', callback_data='dmca')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
            InlineKeyboardButton('Auto Filter', callback_data='autofilter')
        ], [
            InlineKeyboardButton('Connection', callback_data='coct'),
            InlineKeyboardButton('Extra Mods', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔮 Status', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "about":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "source":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='about')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "dmca":
        buttons = [[InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DMCA_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('⏹️ Buttons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "button":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='manuelfilter')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "autofilter":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "coct":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('👮‍♂️ Admin', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "admin":
        buttons = [[InlineKeyboardButton('👩‍🦯 Back', callback_data='extra')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return await safe_answer(query, 'Piracy Is Crime')

    elif query.data == "rfrsh":
        await safe_answer(query, "Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await safe_answer(query, 'Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
        return await safe_answer(query, 'Piracy Is Crime')

    # fallback
    await safe_answer(query, 'Piracy Is Crime')


# ══════════════════════════════════════════════════════════════════════════════
#  AUTO-FILTER
# ══════════════════════════════════════════════════════════════════════════════

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"):
            return
        if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll

    pre = 'filep' if settings['file_secure'] else 'file'

    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    BUTTONS[key] = search
    req = message.from_user.id if message.from_user else 0

    if settings["button"]:
        btn = [
            [InlineKeyboardButton(
                text=f"📁[{get_size(file.file_size)}]-🎭-{file.file_name}",
                callback_data=f'{pre}#{file.file_id}'
            )]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(text=f"{file.file_name}",          callback_data=f'{pre}#{file.file_id}'),
                InlineKeyboardButton(text=f"{get_size(file.file_size)}", callback_data=f'{pre}#{file.file_id}'),
            ]
            for file in files
        ]

    for row in reversed(_filter_rows(key)):
        btn.insert(0, row)

    if offset != "":
        btn.append([
            InlineKeyboardButton(text=f"📃 1/{math.ceil(int(total_results)/10)}", callback_data="pages"),
            InlineKeyboardButton(text="NEXT ▶️", callback_data=f"next_{req}_{key}_{offset}"),
        ])
    else:
        btn.append([InlineKeyboardButton(text="📃 1/1", callback_data="pages")])

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = script.RESULT_TXT.format(search)

    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(
                photo=imdb.get('poster'), caption=cap[:1024],
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(
                photo=poster, caption=cap[:1024],
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))

    if spoll:
        await msg.message.delete()


# ══════════════════════════════════════════════════════════════════════════════
#  SPELL-CHECK
# ══════════════════════════════════════════════════════════════════════════════

async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    cleaned_query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|"
        r"br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|"
        r"kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|"
        r"any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE
    )
    cleaned_query = cleaned_query.strip()

    settings = await get_settings(msg.chat.id)

    try:
        movies = await get_poster(cleaned_query, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = quote_plus(mv_rqst)
        button = [[
            InlineKeyboardButton('ENG', callback_data='esp'),
            InlineKeyboardButton('MAL', callback_data='msp'),
            InlineKeyboardButton('HIN', callback_data='hsp'),
            InlineKeyboardButton('TAM', callback_data='tsp'),
        ], [
            InlineKeyboardButton('🔍 ɢᴏᴏɢʟᴇ 🔎', url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        k = await msg.reply_text(
            text=script.SPOLL_NOT_FND,
            reply_markup=InlineKeyboardMarkup(button),
            reply_to_message_id=msg.id
        )
        await asyncio.sleep(45)
        await k.delete()
        return

    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton('ENG', callback_data='esp'),
            InlineKeyboardButton('MAL', callback_data='msp'),
            InlineKeyboardButton('HIN', callback_data='hsp'),
            InlineKeyboardButton('TAM', callback_data='tsp'),
        ], [
            InlineKeyboardButton('🔍 ɢᴏᴏɢʟᴇ 🔎', url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        k = await msg.reply_text(
            text=script.SPOLL_NOT_FND,
            reply_markup=InlineKeyboardMarkup(button),
            reply_to_message_id=msg.id
        )
        await asyncio.sleep(60)
        await k.delete()
        return

    movielist = [movie.get('title') for movie in movies]
    movielist = [title for title in movielist if title]
    if not movielist:
        return

    SPELL_CHECK[mv_id] = movielist
    btn = [
        [InlineKeyboardButton(
            text=movie_name.strip(),
            callback_data=f"spol#{reqstr1}#{k}",
        )]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="✘ ᴄʟᴏsᴇ ✘", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_text(
        text="<b>Sᴘᴇʟʟɪɴɢ Mɪꜱᴛᴀᴋᴇ Bʀᴏ ‼️\n\nᴅᴏɴ'ᴛ ᴡᴏʀʀʏ 😊 Cʜᴏᴏꜱᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴏɴᴇ ʙᴇʟᴏᴡ 👇</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        reply_to_message_id=msg.id
    )
    await asyncio.sleep(50)
    await spell_check_del.delete()


# ══════════════════════════════════════════════════════════════════════════════
#  MANUAL FILTERS
# ══════════════════════════════════════════════════════════════════════════════

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
