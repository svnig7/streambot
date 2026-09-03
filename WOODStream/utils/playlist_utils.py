import asyncio
import logging

from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from WOODStream.bot import multi_clients
from WOODStream.config import Telegram, Server
from WOODStream.utils.database import Database
from WOODStream.utils.file_properties import get_file_ids, get_file_info, get_media_from_message, get_name
from WOODStream.utils.bot_utils import gen_playlist_link
from WOODStream.utils.tokens import new_token

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

# Telegram delivers each item of an album as a separate update sharing one
# media_group_id. We only want to build the playlist once per album, so the
# first update to see a given group_id claims it and the rest bail out early.
_albums_seen = set()
_albums_lock = asyncio.Lock()

# How long to wait for the rest of an album's items to arrive before reading
# it back with get_media_group(). Telegram normally delivers all items of an
# album within a second of each other.
_ALBUM_SETTLE_SECONDS = 1.5


async def _claim_album(group_id) -> bool:
    async with _albums_lock:
        if group_id in _albums_seen:
            return False
        _albums_seen.add(group_id)
        return True


def _release_album(group_id):
    _albums_seen.discard(group_id)


async def _mint_playlist(bot, message, owner_id):
    """Reads back the whole album via get_media_group(), stores each playable
    item as a normal streambot file (tagged with a shared playlist token),
    and returns (token, minted_ids, first_name) or (None, [], None)."""
    try:
        items = await bot.get_media_group(message.chat.id, message.id)
    except Exception as e:
        logging.error(f"Failed reading back album {message.media_group_id}: {e}")
        return None, [], None

    items = items[: Telegram.MAX_PLAYLIST_ITEMS]
    token = new_token()
    minted = []
    first_name = None

    for idx, item in enumerate(items):
        if not get_media_from_message(item):
            continue
        try:
            info = get_file_info(item)
            info["pl"] = token
            info["pi"] = idx
            inserted_id = await db.add_file(info)
            await get_file_ids(False, inserted_id, multi_clients, item)
        except Exception as e:
            logging.error(f"Skipping album item {item.id}: {e}")
            continue
        minted.append(str(inserted_id))
        if first_name is None:
            first_name = get_name(item)

    if not minted:
        return None, [], None

    await db.add_playlist(token, first_name or "Playlist", minted, owner_id=owner_id)
    return token, minted, first_name


async def handle_private_album(bot, message):
    """Called instead of the normal single-file flow when a private upload
    is part of an album. Merged in from telestream-bot's `-pl` flag."""
    group_id = message.media_group_id
    if not await _claim_album(group_id):
        return
    try:
        await asyncio.sleep(_ALBUM_SETTLE_SECONDS)
        token, minted, _ = await _mint_playlist(bot, message, owner_id=message.from_user.id)
        if not token:
            return
        reply_markup, text = await gen_playlist_link(token)
        await message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
            quote=True,
        )
    finally:
        _release_album(group_id)


async def handle_channel_album(bot, message):
    """Channel equivalent of handle_private_album: mints one playlist for the
    whole album and edits the album item that triggered this handler with a
    single 'stream / download' button pointing at the playlist."""
    group_id = message.media_group_id
    if not await _claim_album(group_id):
        return
    try:
        await asyncio.sleep(_ALBUM_SETTLE_SECONDS)
        token, minted, _ = await _mint_playlist(bot, message, owner_id=message.chat.id)
        if not token:
            return
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=message.id,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        "sᴛʀᴇᴀᴍ / ᴅᴏᴡɴʟᴏᴀᴅ (ᴘʟᴀʏʟɪsᴛ)",
                        url=f"{Server.URL}playlist/{token}",
                    )]]
                ),
            )
        except Exception as e:
            logging.error(f"Can't edit album message in channel {message.chat.id}: {e}")
    finally:
        _release_album(group_id)
