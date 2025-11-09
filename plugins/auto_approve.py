#CREDITS GOTO GOUTHAMSER !!!!!!!!!!!
#@im_goutham_josh    tg user
# add to group or channel and gives admin rights only

import os
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, Message
from info import ADMINS

# ✅ Default auto-approve state (from .env)
AUTO_APPROVE = os.getenv("AUTO_APPROVE", "ON").upper() == "ON"

# ✅ Default welcome DM state (from .env)
WELCOME_DM = os.getenv("WELCOME_DM", "OFF").upper() == "OFF"

# ✅ Multiple admin IDs allowed (space-separated)
ADMINS = [int(i) for i in os.getenv("ADMINS", "").split()]  # e.g., "123456789 987654321"


# --- AUTO APPROVE HANDLER ---
@Client.on_chat_join_request()
async def auto_approve(client, join_request: ChatJoinRequest):
    global AUTO_APPROVE, WELCOME_DM

    if not AUTO_APPROVE:
        print("🚫 Auto-approval is OFF — ignoring join requests.")
        return

    try:
        # Approve the user
        await client.approve_chat_join_request(join_request.chat.id, join_request.from_user.id)
        print(f"✅ Approved: {join_request.from_user.first_name} ({join_request.from_user.id})")

        # ✅ Send DM welcome message (only if enabled)
        if WELCOME_DM:
            try:
                await client.send_message(
                    chat_id=join_request.from_user.id,
                    text=f"🎉 You’ve been approved to join **{join_request.chat.title}**!\n\nEnjoy your stay 😄"
                )
                print(f"✉️ Sent welcome DM to {join_request.from_user.first_name}")
            except Exception as pm_error:
                print(f"⚠️ Couldn't DM {join_request.from_user.first_name}: {pm_error}")

    except Exception as e:
        print(f"❌ Error approving {join_request.from_user.id}: {e}")


# --- ADMIN COMMANDS ---
@Client.on_message(filters.private & filters.user(ADMINS) & filters.command(["approve_on", "approve_off"]))
async def toggle_auto_approve(client, message: Message):
    global AUTO_APPROVE

    if message.command[0] == "approve_on":
        AUTO_APPROVE = True
        await message.reply_text("✅ Auto-approval has been **ENABLED**.")
        print("🔛 Auto-approval enabled by admin.")
    elif message.command[0] == "approve_off":
        AUTO_APPROVE = False
        await message.reply_text("🚫 Auto-approval has been **DISABLED**.")
        print("🔴 Auto-approval disabled by admin.")


# --- WELCOME DM TOGGLE COMMANDS ---
@Client.on_message(filters.private & filters.user(ADMINS) & filters.command(["welcome_on", "welcome_off"]))
async def toggle_welcome_dm(client, message: Message):
    global WELCOME_DM

    if message.command[0] == "welcome_on":
        WELCOME_DM = True
        await message.reply_text("👋 Welcome DM has been **ENABLED**.")
        print("💬 Welcome DM enabled by admin.")
    elif message.command[0] == "welcome_off":
        WELCOME_DM = False
        await message.reply_text("🤫 Welcome DM has been **DISABLED**.")
        print("🚫 Welcome DM disabled by admin.")


# --- STATUS COMMAND ---
@Client.on_message(filters.private & filters.user(ADMINS) & filters.command(["approve_status"]))
async def check_status(client, message: Message):
    approve_status = "✅ ON" if AUTO_APPROVE else "❌ OFF"
    welcome_status = "✅ ON" if WELCOME_DM else "❌ OFF"

    await message.reply_text(
        f"⚙️ **Current Settings:**\n"
        f"• Auto-Approval: {approve_status}\n"
        f"• Welcome DM: {welcome_status}"
    )
