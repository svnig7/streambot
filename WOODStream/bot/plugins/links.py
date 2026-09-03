import time

from pyrogram import filters, Client
from pyrogram.types import Message

from WOODStream.bot import WOODStream
from WOODStream.config import Telegram
from WOODStream.utils.database import Database
from WOODStream.utils.bot_utils import file_id_from_message
from WOODStream.utils.tokens import parse_duration
from WOODStream.utils.time_format import get_readable_time
from WOODStream.server.exceptions import FIleNotFound

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


def _is_owner(file_info, message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else message.chat.id
    return user_id == file_info.get("user_id") or user_id == Telegram.OWNER_ID


async def _resolve_target(message: Message):
    """/ttl and /poster act on whichever file link the command replies to."""
    reply = message.reply_to_message
    if not reply:
        await message.reply_text(
            "**ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ ᴏғ ᴍʏ ʟɪɴᴋ ᴍᴇssᴀɢᴇs ᴡɪᴛʜ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ**",
            quote=True,
        )
        return None
    file_id = file_id_from_message(reply)
    if not file_id:
        await message.reply_text(
            "**ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ ᴀ ʟɪɴᴋ ɪɴ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ**",
            quote=True,
        )
        return None
    try:
        file_info = await db.get_file(file_id)
    except FIleNotFound:
        await message.reply_text("**ғɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ (ᴀʟʀᴇᴀᴅʏ ᴅᴇʟᴇᴛᴇᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ)**", quote=True)
        return None
    if not _is_owner(file_info, message):
        await message.reply_text("**ᴏɴʟʏ ᴛʜᴇ ᴜᴘʟᴏᴀᴅᴇʀ (ᴏʀ ᴏᴡɴᴇʀ) ᴄᴀɴ ᴄʜᴀɴɢᴇ ᴛʜɪs**", quote=True)
        return None
    return file_id, file_info


@WOODStream.on_message(filters.command("ttl") & filters.private)
async def set_ttl(bot: Client, message: Message):
    target = await _resolve_target(message)
    if not target:
        return
    file_id, file_info = target

    arg = message.command[1] if len(message.command) > 1 else ""
    if arg.strip().lower() in ("0", "off", "none", "clear"):
        await db.set_ttl(file_id, None)
        await message.reply_text("**ᴛᴛʟ ʀᴇᴍᴏᴠᴇᴅ, ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ**", quote=True)
        return

    seconds = parse_duration(arg)
    if seconds <= 0:
        await message.reply_text(
            "**ᴜsᴀɢᴇ :** `/ttl 1d2h` (ᴅ/ʜ/ᴍ/s) ᴏʀ `/ttl off` ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀɴ ᴇxɪsᴛɪɴɢ ᴛᴛʟ",
            quote=True,
        )
        return

    exp = time.time() + seconds
    await db.set_ttl(file_id, exp)
    await message.reply_text(
        f"**ʟɪɴᴋ ᴡɪʟʟ ᴇxᴘɪʀᴇ ɪɴ** `{get_readable_time(seconds)}`",
        quote=True,
    )


@WOODStream.on_message(filters.command(["poster", "thumb"]) & filters.private)
async def set_poster(bot: Client, message: Message):
    target = await _resolve_target(message)
    if not target:
        return
    file_id, file_info = target

    if len(message.command) < 2:
        await message.reply_text("**ᴜsᴀɢᴇ :** `/poster https://image.url`", quote=True)
        return
    url = message.command[1]
    if not url.lower().startswith(("http://", "https://")):
        await message.reply_text("**ᴛʜᴀᴛ ᴅᴏᴇsɴ'ᴛ ʟᴏᴏᴋ ʟɪᴋᴇ ᴀ ᴠᴀʟɪᴅ ɪᴍᴀɢᴇ ᴜʀʟ**", quote=True)
        return

    await db.set_poster(file_id, url)
    await message.reply_text("**ᴄᴏᴠᴇʀ ᴀʀᴛ ᴜᴘᴅᴀᴛᴇᴅ**", quote=True)
