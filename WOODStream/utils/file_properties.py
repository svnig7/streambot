from __future__ import annotations
import html
import logging
from datetime import datetime
from pyrogram import Client
from typing import Any, Optional

from pyrogram.enums import ParseMode, ChatType
from pyrogram.types import Message
from pyrogram.file_id import FileId
from WOODStream.bot import WOODStream
from WOODStream.utils.database import Database
from WOODStream.config import Telegram, Server

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


async def get_file_ids(client: Client | bool, db_id: str, multi_clients, message) -> Optional[FileId]:
    logging.debug("Starting of get_file_ids")
    file_info = await db.get_file(db_id)
    if (not "file_ids" in file_info) or not client:
        logging.debug("Storing file_id of all clients in DB")
        log_msg = await send_file(WOODStream, db_id, file_info['file_id'], message)
        await db.update_file_ids(db_id, await update_file_id(log_msg.id, multi_clients))
        logging.debug("Stored file_id of all clients in DB")
        if not client:
            return
        file_info = await db.get_file(db_id)

    file_id_info = file_info.setdefault("file_ids", {})
    if not str(client.id) in file_id_info:
        logging.debug("Storing file_id in DB")
        log_msg = await send_file(WOODStream, db_id, file_info['file_id'], message)
        msg = await client.get_messages(Telegram.FLOG_CHANNEL, log_msg.id)
        media = get_media_from_message(msg)
        file_id_info[str(client.id)] = getattr(media, "file_id", "")
        await db.update_file_ids(db_id, file_id_info)
        logging.debug("Stored file_id in DB")

    logging.debug("Middle of get_file_ids")
    file_id = FileId.decode(file_id_info[str(client.id)])
    setattr(file_id, "file_size", file_info['file_size'])
    setattr(file_id, "mime_type", file_info['mime_type'])
    setattr(file_id, "file_name", file_info['file_name'])
    setattr(file_id, "unique_id", file_info['file_unique_id'])
    logging.debug("Ending of get_file_ids")
    return file_id


def get_media_from_message(message: "Message") -> Any:
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media


def get_media_file_size(m):
    media = get_media_from_message(m)
    return getattr(media, "file_size", "None")


def get_name(media_msg: Message | FileId) -> str:
    if isinstance(media_msg, Message):
        media = get_media_from_message(media_msg)
        file_name = getattr(media, "file_name", "")

    elif isinstance(media_msg, FileId):
        file_name = getattr(media_msg, "file_name", "")

    if not file_name:
        if isinstance(media_msg, Message) and media_msg.media:
            media_type = media_msg.media.value
        elif media_msg.file_type:
            media_type = media_msg.file_type.name.lower()
        else:
            media_type = "file"

        formats = {
            "photo": "jpg", "audio": "mp3", "voice": "ogg",
            "video": "mp4", "animation": "mp4", "video_note": "mp4",
            "sticker": "webp"
        }

        ext = formats.get(media_type)
        ext = "." + ext if ext else ""

        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{media_type}-{date}{ext}"

    return file_name


def get_file_info(message):
    media = get_media_from_message(message)
    if message.chat.type == ChatType.PRIVATE:
        user_idx = message.from_user.id
    else:
        user_idx = message.chat.id
    # Original caption (if any) is preserved so the bot's reply can reuse
    # whatever rich formatting (title/plot/etc.) was already on the upload,
    # instead of the bot inventing its own metadata.
    caption_html = message.caption.html if getattr(message, "caption", None) else None
    # Custom cover/thumbnail (e.g. a movie poster attached to the video) is
    # captured so it can be reproduced exactly on resend, instead of Telegram
    # falling back to an auto-extracted video frame.
    thumbs = getattr(media, "thumbs", None)
    cover_file_id = thumbs[-1].file_id if thumbs else None
    return {
        "user_id": user_idx,
        "file_id": getattr(media, "file_id", ""),
        "file_unique_id": getattr(media, "file_unique_id", ""),
        "file_name": get_name(message),
        "file_size": getattr(media, "file_size", 0),
        "mime_type": getattr(media, "mime_type", "None/unknown"),
        "caption_html": caption_html,
        "cover_file_id": cover_file_id,
        "kind": message.media.value if message.media else None,
    }


def build_resend_caption(file_info: dict) -> str:
    """Filename plus the original metadata caption (if any), used whenever
    the bot resends a file (Get File, and the FLOG_CHANNEL log copy) -
    plain text, no forced code/blockquote formatting."""
    file_name = file_info.get("file_name") or ""
    parts = [html.escape(file_name)]
    caption_html = file_info.get("caption_html")
    if caption_html:
        parts.append(caption_html)
    return "\n\n".join(parts)


async def resend_media(client: Client, chat_id, file_info: dict, reply_to_message_id=None, caption_override=None):
    """Resends a stored file exactly as it was originally uploaded - same
    caption, same cover/thumbnail. Used as a fallback when a file predates
    log_msg_id (see copy_stored_file below).

    Tries the newer `cover=` parameter first (Bot API's dedicated video
    cover), then falls back to the classic `thumb=` parameter, mirroring the
    approach of the video-cover-bot snippet this was ported from - some
    Pyrogram builds don't have `cover=` yet, so the fallback keeps this
    working everywhere.
    """
    file_id = file_info["file_id"]
    kind = file_info.get("kind")
    cover = file_info.get("cover_file_id")
    caption = caption_override if caption_override is not None else build_resend_caption(file_info)

    base = dict(chat_id=chat_id, caption=caption, parse_mode=ParseMode.HTML)
    if reply_to_message_id:
        base["reply_to_message_id"] = reply_to_message_id

    if kind == "video" and cover:
        try:
            return await client.send_video(video=file_id, cover=cover, supports_streaming=True, **base)
        except TypeError:
            pass
        except Exception as e:
            logging.debug(f"send_video(cover=...) failed, falling back to thumb=: {e}")
        try:
            return await client.send_video(video=file_id, thumb=cover, supports_streaming=True, **base)
        except Exception as e:
            logging.debug(f"send_video(thumb=...) failed, falling back to cached media: {e}")
    elif kind == "audio" and cover:
        try:
            return await client.send_audio(audio=file_id, thumb=cover, **base)
        except Exception as e:
            logging.debug(f"send_audio(thumb=...) failed, falling back to cached media: {e}")
    elif kind == "animation" and cover:
        try:
            return await client.send_animation(animation=file_id, thumb=cover, **base)
        except Exception as e:
            logging.debug(f"send_animation(thumb=...) failed, falling back to cached media: {e}")

    return await client.send_cached_media(file_id=file_id, **base)


async def update_file_id(msg_id, multi_clients):
    file_ids = {}
    for client_id, client in multi_clients.items():
        log_msg = await client.get_messages(Telegram.FLOG_CHANNEL, msg_id)
        media = get_media_from_message(log_msg)
        file_ids[str(client.id)] = getattr(media, "file_id", "")

    return file_ids


async def send_file(client: Client, db_id, file_id: str, message):
    """Logs the upload into FLOG_CHANNEL by copying the original message
    directly - .copy() reproduces the exact cover/thumbnail, which
    reconstructing via file_id + an explicit thumb= parameter wasn't
    reliably preserving. The caption is overridden with the standard
    code-filename + collapsible-blockquote format rather than whatever
    entities the original happened to carry, so it's consistent everywhere
    the file gets resent (merged in per user request)."""
    file_info = await db.get_file(db_id)
    caption = build_resend_caption(file_info)
    log_msg = await message.copy(Telegram.FLOG_CHANNEL, caption=caption, parse_mode=ParseMode.HTML)

    if not file_info.get("log_msg_id"):
        await db.set_log_message(db_id, log_msg.id)

    if message.chat.type == ChatType.PRIVATE:
        await log_msg.reply_text(
            text=f"**Requested by :** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**User ID :** `{message.from_user.id}`\n**File ID :** `{db_id}`",
            disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
    else:
        await log_msg.reply_text(
            text=f"**Requested by :** {message.chat.title} \n**Channel ID :** `{message.chat.id}`\n**File ID :** `{db_id}`",
            disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)

    return log_msg


async def copy_stored_file(client: Client, chat_id, file_info: dict, reply_to_message_id=None):
    """Used by every 'Get File' button. Copies the file's FLOG_CHANNEL log
    message (which is itself a direct .copy() of the original upload, with
    the caption already overridden - see send_file above), so the cover and
    caption always come out identical to what was originally sent."""
    caption = build_resend_caption(file_info)
    log_msg_id = file_info.get("log_msg_id")
    if log_msg_id:
        try:
            source = await client.get_messages(Telegram.FLOG_CHANNEL, log_msg_id)
            if source and not source.empty:
                return await source.copy(chat_id=chat_id, caption=caption, parse_mode=ParseMode.HTML,
                                          reply_to_message_id=reply_to_message_id)
        except Exception as e:
            logging.debug(f"Copy from FLOG_CHANNEL failed for a file, falling back: {e}")
    # Older records that predate log_msg_id, or a channel that's since been
    # cleared - fall back to the file_id + cover/thumb reconstruction.
    return await resend_media(client, chat_id, file_info, reply_to_message_id=reply_to_message_id,
                               caption_override=caption)

