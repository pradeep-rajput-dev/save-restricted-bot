import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageIdInvalid, ChannelPrivate
import re

# ============ CONFIG ============
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
# ================================

# Bot client (for sending messages to user)
bot = Client(
    "save_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# User client (for accessing restricted content)
user = Client(
    "user_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)


def parse_link(link: str):
    """Parse Telegram link and return (chat_id_or_username, message_id)"""
    # https://t.me/username/123
    # https://t.me/c/1234567890/123
    
    private_pattern = r"https://t\.me/c/(\d+)/(\d+)"
    public_pattern = r"https://t\.me/([^/]+)/(\d+)"
    
    private_match = re.match(private_pattern, link)
    if private_match:
        chat_id = int("-100" + private_match.group(1))
        msg_id = int(private_match.group(2))
        return chat_id, msg_id
    
    public_match = re.match(public_pattern, link)
    if public_match:
        username = public_match.group(1)
        msg_id = int(public_match.group(2))
        return username, msg_id
    
    return None, None


@bot.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text(
        "**🔓 Save Restricted Bot**\n\n"
        "Kisi bhi restricted Telegram post ka link bhejo — main download karke bhej dunga!\n\n"
        "**Supported:**\n"
        "• Private channel links\n"
        "• Public channel restricted posts\n"
        "• Photos, Videos, Documents, Audio\n\n"
        "**Usage:**\n"
        "Simply paste the `t.me` link here ✅"
    )


@bot.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        "**How to use:**\n\n"
        "1. Copy the post link from any Telegram channel\n"
        "2. Paste it here\n"
        "3. Bot will download and send you the file\n\n"
        "**Link formats supported:**\n"
        "`https://t.me/channelname/123`\n"
        "`https://t.me/c/1234567890/123`\n\n"
        "⚠️ Make sure your userbot has joined the channel!"
    )


@bot.on_message(filters.text & filters.private)
async def handle_link(client: Client, message: Message):
    link = message.text.strip()
    
    if not link.startswith("https://t.me/"):
        await message.reply_text("❌ Valid Telegram link bhejo!\n\nFormat: `https://t.me/...`")
        return
    
    chat_id, msg_id = parse_link(link)
    
    if not chat_id or not msg_id:
        await message.reply_text("❌ Link format sahi nahi hai. Valid t.me link bhejo.")
        return
    
    status_msg = await message.reply_text("⏳ Fetching content...")
    
    try:
        # Use userbot to get the message
        async with user:
            try:
                source_msg = await user.get_messages(chat_id, msg_id)
            except ChannelPrivate:
                await status_msg.edit("❌ Userbot ne is channel ko join nahi kiya hai!\n\nPehle userbot se channel join karo.")
                return
            except MessageIdInvalid:
                await status_msg.edit("❌ Message nahi mila. Link check karo.")
                return
            
            if not source_msg:
                await status_msg.edit("❌ Message nahi mila.")
                return
            
            # Forward/copy based on content type
            if source_msg.media:
                await status_msg.edit("📥 Downloading...")
                
                try:
                    # Copy message directly (fastest method)
                    await source_msg.copy(message.chat.id)
                    await status_msg.edit("✅ Done!")
                except Exception:
                    # Fallback: download then send
                    await status_msg.edit("📥 Downloading file...")
                    file_path = await user.download_media(source_msg)
                    
                    await status_msg.edit("📤 Uploading...")
                    
                    caption = source_msg.caption or ""
                    
                    if source_msg.video:
                        await bot.send_video(message.chat.id, file_path, caption=caption)
                    elif source_msg.photo:
                        await bot.send_photo(message.chat.id, file_path, caption=caption)
                    elif source_msg.document:
                        await bot.send_document(message.chat.id, file_path, caption=caption)
                    elif source_msg.audio:
                        await bot.send_audio(message.chat.id, file_path, caption=caption)
                    elif source_msg.voice:
                        await bot.send_voice(message.chat.id, file_path, caption=caption)
                    elif source_msg.video_note:
                        await bot.send_video_note(message.chat.id, file_path)
                    elif source_msg.sticker:
                        await bot.send_sticker(message.chat.id, file_path)
                    else:
                        await bot.send_document(message.chat.id, file_path, caption=caption)
                    
                    # Clean up downloaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    await status_msg.edit("✅ Done!")
            
            elif source_msg.text:
                await bot.send_message(message.chat.id, source_msg.text)
                await status_msg.edit("✅ Done!")
            
            else:
                await status_msg.edit("❌ Is message mein koi content nahi mila.")
    
    except FloodWait as e:
        await status_msg.edit(f"⏳ Flood wait: {e.value} seconds ruko...")
        await asyncio.sleep(e.value)
        await status_msg.edit("✅ Try again karo.")
    
    except Exception as e:
        await status_msg.edit(f"❌ Error: `{str(e)}`")


async def main():
    await bot.start()
    print("Bot started!")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
