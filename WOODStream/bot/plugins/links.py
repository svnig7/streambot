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
            "**Reply to one of my link messages with this command**",
            quote=True,
        )
        return None
    file_id = file_id_from_message(reply)
    if not file_id:
        await message.reply_text(
            "**Couldn't find a link in that message**",
            quote=True,
        )
        return None
    try:
        file_info = await db.get_file(file_id)
    except FIleNotFound:
        await message.reply_text("**File not found (already deleted or expired)**", quote=True)
        return None
    if not _is_owner(file_info, message):
        await message.reply_text("**Only the uploader (or owner) can change this**", quote=True)
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
        await message.reply_text("**TTL removed, link won't expire**", quote=True)
        return

    seconds = parse_duration(arg)
    if seconds <= 0:
        await message.reply_text(
            "**Usage:** `/ttl 1d2h` (d/h/m/s) or `/ttl off` to remove an existing TTL",
            quote=True,
        )
        return

    exp = time.time() + seconds
    await db.set_ttl(file_id, exp)
    await message.reply_text(
        f"**Link will expire in** `{get_readable_time(seconds)}`",
        quote=True,
    )


@WOODStream.on_message(filters.command(["poster", "thumb"]) & filters.private)
async def set_poster(bot: Client, message: Message):
    target = await _resolve_target(message)
    if not target:
        return
    file_id, file_info = target

    if len(message.command) < 2:
        await message.reply_text("**Usage:** `/poster https://image.url`", quote=True)
        return
    url = message.command[1]
    if not url.lower().startswith(("http://", "https://")):
        await message.reply_text("**That doesn't look like a valid image URL**", quote=True)
        return

    await db.set_poster(file_id, url)
    await message.reply_text("**Cover art updated**", quote=True)
