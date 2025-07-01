from pyrogram.errors import UserNotParticipant, FloodWait
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from WOODStream.utils.translation import LANG
from WOODStream.utils.database import Database
from WOODStream.utils.human_readable import humanbytes
from WOODStream.config import Telegram, Server
from WOODStream.bot import WOODStream
import asyncio
from typing import (
    Union
)

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

async def is_user_joined(bot, message: Message):
    required_chats = []

    if Telegram.FORCE_SUB_ID:
        required_chats.append(("channel", Telegram.FORCE_SUB_ID, Telegram.FORCE_SUB_LINK))
    if hasattr(Telegram, 'FORCE_SUB_GROUP_ID') and Telegram.FORCE_SUB_GROUP_ID:
        required_chats.append(("group", Telegram.FORCE_SUB_GROUP_ID, Telegram.FORCE_SUB_GROUP_LINK))

    for chat_type, chat_id, invite_link in required_chats:
        if chat_id.startswith("-100"):
            chat_id = int(chat_id)

        try:
            member = await bot.get_chat_member(chat_id, message.from_user.id)
            if member.status == "BANNED":
                await message.reply_text(
                    text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                return False
        except UserNotParticipant:
            buttons = []
            if Telegram.FORCE_SUB_ID:
                buttons.append(InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=Telegram.FORCE_SUB_LINK))
            if Telegram.FORCE_SUB_GROUP_ID:
                buttons.append(InlineKeyboardButton("👥 ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=Telegram.FORCE_SUB_GROUP_LINK))

            # Add Refresh button in new row
            buttons_markup = [buttons, [InlineKeyboardButton("✅ ʀᴇғʀᴇsʜ", callback_data="refresh_join")]]

            if Telegram.VERIFY_PIC:
                ver = await message.reply_photo(
                    photo=Telegram.VERIFY_PIC,
                    caption="ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ɢʀᴏᴜᴘ ᴛᴏ ᴜsᴇ ᴍᴇ 🔐",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(buttons_markup)
                )
            else:
                ver = await message.reply_text(
                    text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ʙᴏᴛʜ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ 🔐</b>",
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(buttons_markup)
                )
            return False
        except Exception:
            await message.reply_text(
                text=f"⚠️ ᴇʀʀᴏʀ. ᴄᴏɴᴛᴀᴄᴛ <a href='https://t.me/cntct_7bot'>ᴅᴇᴠᴇʟᴏᴘᴇʀ</a>",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            return False

    return True
    
#---------------------[ PRIVATE GEN LINK + CALLBACK ]---------------------#

async def gen_link(_id):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    file_size = humanbytes(file_info['file_size'])
    mime_type = file_info['mime_type']

    page_link = f"{Server.URL}watch/{_id}"
    stream_link = f"{Server.URL}dl/{_id}"
    file_link = f"{Server.URL}file/{_id}"
    deep_link = f"https://t.me/{WOODStream.username}?start=file_{_id}"

    if "video" in mime_type:
        stream_text = LANG.STREAM_TEXT.format(file_name, file_size, page_link, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("sᴛʀᴇᴀᴍ", url=page_link), InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ", url=file_link), InlineKeyboardButton("ʀᴇᴠᴏᴋᴇ", callback_data=f"msgdelpvt_{_id}")],
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ]
        )
    else:
        stream_text = LANG.STREAM_TEXT_X.format(file_name, file_size, page_link, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ", url=file_link), InlineKeyboardButton("ʀᴇᴠᴏᴋᴇ", callback_data=f"msgdelpvt_{_id}")],
                [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
            ]
        )
    return reply_markup, stream_text

#---------------------[ GEN STREAM LINKS FOR CHANNEL ]---------------------#

async def gen_linkx(m:Message , _id, name: list):
    file_info = await db.get_file(_id)
    file_name = file_info['file_name']
    mime_type = file_info['mime_type']
    file_size = humanbytes(file_info['file_size'])

    page_link = f"{Server.URL}watch/{_id}"
    stream_link = f"{Server.URL}dl/{_id}"
    file_link = f"{Server.URL}file/{_id}"
    deep_link = f"https://t.me/{WOODStream.username}?start=file_{_id}"

    if "video" in mime_type:
        stream_text= LANG.STREAM_TEXT_X.format(file_name, file_size, page_link, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("sᴛʀᴇᴀᴍ", url=page_link), InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ", url=file_link)]
            ]
        )
    else:
        stream_text= LANG.STREAM_TEXT_X.format(file_name, file_size, page_link, stream_link, file_link)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ", url=stream_link)],
                [InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ", url=file_link)]
            ]
        )
    return reply_markup, stream_text

#---------------------[ USER BANNED ]---------------------#

async def is_user_banned(message):
    if await db.is_user_banned(message.from_user.id):
        await message.reply_text(
            text=LANG.BAN_TEXT.format(Telegram.OWNER_ID),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        return True
    return False

#---------------------[ CHANNEL BANNED ]---------------------#

async def is_channel_banned(bot, message):
    if await db.is_user_banned(message.chat.id):
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(f"ᴄʜᴀɴɴᴇʟ ɪs ʙᴀɴɴᴇᴅ", callback_data="N/A")]])
        )
        return True
    return False

#---------------------[ USER AUTH ]---------------------#

async def is_user_authorized(message):
    if hasattr(Telegram, 'AUTH_USERS') and Telegram.AUTH_USERS:
        user_id = message.from_user.id

        if user_id == Telegram.OWNER_ID:
            return True

        if not (user_id in Telegram.AUTH_USERS):
            await message.reply_text(
                text="ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ.",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            return False

    return True

#---------------------[ USER EXIST ]---------------------#

async def is_user_exist(bot, message):
    if not bool(await db.get_user(message.from_user.id)):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Telegram.ULOG_CHANNEL,
            f"**#ɴᴇᴡᴜsᴇʀ**\n**⬩ ᴜsᴇʀ ɴᴀᴍᴇ :** [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n**⬩ ᴜsᴇʀ ɪᴅ :** `{message.from_user.id}`"
        )

async def is_channel_exist(bot, message):
    if not bool(await db.get_user(message.chat.id)):
        await db.add_user(message.chat.id)
        members = await bot.get_chat_members_count(message.chat.id)
        await bot.send_message(
            Telegram.ULOG_CHANNEL,
            f"**#ɴᴇᴡᴄʜᴀɴɴᴇʟ** \n**⬩ ᴄʜᴀᴛ ɴᴀᴍᴇ :** `{message.chat.title}`\n**⬩ ᴄʜᴀᴛ ɪᴅ :** `{message.chat.id}`\n**⬩ ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs :** `{members}`"
        )

async def verify_user(bot, message):
    if not await is_user_authorized(message):
        return False

    if await is_user_banned(message):
        return False

    await is_user_exist(bot, message)

    if Telegram.FORCE_SUB:
        if not await is_user_joined(bot, message):
            return False

    return True
