import os
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, Message
from info import ADMINS

# ✅ Default auto-approve state (read from environment variable)
AUTO_APPROVE = os.getenv("AUTO_APPROVE", "ON").upper() == "ON"

# ✅ Multiple admin IDs allowed (comma-separated in .env)
ADMINS = [int(i) for i in os.getenv("ADMINS", "").split()]  # e.g., "123456789 987654321"


# --- AUTO APPROVE HANDLER ---
@Client.on_chat_join_request()
async def auto_approve(client, join_request: ChatJoinRequest):
    global AUTO_APPROVE

    if not AUTO_APPROVE:
        print("🚫 Auto-approval is OFF — ignoring join requests.")
        return

    try:
        await client.approve_chat_join_request(join_request.chat.id, join_request.from_user.id)
        print(f"✅ Approved: {join_request.from_user.first_name} ({join_request.from_user.id})")

        # Send welcome message in group
        await client.send_message(
            chat_id=join_request.chat.id,
            text=f"👋 Welcome [{join_request.from_user.first_name}](tg://user?id={join_request.from_user.id})!\nGlad to have you here 😊",
            disable_web_page_preview=True
        )

        # DM user (optional)
        try:
            await client.send_message(
                chat_id=join_request.from_user.id,
                text=f"🎉 You’ve been approved to join **{join_request.chat.title}**!\nEnjoy your stay 😄"
            )
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


# --- CHECK STATUS ---
@Client.on_message(filters.private & filters.user(ADMINS) & filters.command(["approve_status"]))
async def check_status(client, message: Message):
    status = "✅ ON" if AUTO_APPROVE else "❌ OFF"
    await message.reply_text(f"⚙️ Current Auto-Approval Status: **{status}**")
