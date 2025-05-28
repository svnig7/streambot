import os
import time
import string
import random
import asyncio
import aiofiles
import datetime

from WOODStream.utils.broadcast_helper import send_msg
from WOODStream.utils.database import Database
from WOODStream.bot import WOODStream
from WOODStream.server.exceptions import FIleNotFound
from WOODStream.config import Telegram, Server
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums.parse_mode import ParseMode

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)
broadcast_ids = {}


@WOODStream.on_message(filters.command("status") & filters.private & filters.user(Telegram.OWNER_ID))
async def sts(c: Client, m: Message):
    await m.reply_text(text=f"""**ᴛᴏᴛᴀʟ ᴜsᴇʀs ɪɴ ᴅʙ :** `{await db.total_users_count()}`
**ʙᴀɴɴᴇᴅ ᴜsᴇʀs ɪɴ ᴅʙ :** `{await db.total_banned_users_count()}`
**ᴛᴏᴛᴀʟ ʟɪɴᴋs ɢᴇɴᴇʀᴀᴛᴇᴅ : ** `{await db.total_files()}`"""
                       , parse_mode=ParseMode.MARKDOWN, quote=True)


@WOODStream.on_message(filters.command("ban") & filters.private & filters.user(Telegram.OWNER_ID))
async def sts(b, m: Message):
    id = m.text.split("/ban ")[-1]
    if not await db.is_user_banned(int(id)):
        try:
            await db.ban_user(int(id))
            await db.delete_user(int(id))
            await m.reply_text(text=f"`{id}`** ɪs ʙᴀɴɴᴇᴅ** ", parse_mode=ParseMode.MARKDOWN, quote=True)
            if not str(id).startswith('-100'):
                await b.send_message(
                    chat_id=id,
                    text="**ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ**",
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
        except Exception as e:
            await m.reply_text(text=f"**sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ : {e}** ", parse_mode=ParseMode.MARKDOWN, quote=True)
    else:
        await m.reply_text(text=f"`{id}`** ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ** ", parse_mode=ParseMode.MARKDOWN, quote=True)


@WOODStream.on_message(filters.command("unban") & filters.private & filters.user(Telegram.OWNER_ID))
async def sts(b, m: Message):
    id = m.text.split("/unban ")[-1]
    if await db.is_user_banned(int(id)):
        try:
            await db.unban_user(int(id))
            await m.reply_text(text=f"`{id}`** ɪs ᴜɴʙᴀɴɴᴇᴅ** ", parse_mode=ParseMode.MARKDOWN, quote=True)
            if not str(id).startswith('-100'):
                await b.send_message(
                    chat_id=id,
                    text="**ʏᴏᴜ ᴀʀᴇ ᴜɴʙᴀɴɴᴇᴅ, ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ**",
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
        except Exception as e:
            await m.reply_text(text=f"** sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ : {e}**", parse_mode=ParseMode.MARKDOWN, quote=True)
    else:
        await m.reply_text(text=f"`{id}`** ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ** ", parse_mode=ParseMode.MARKDOWN, quote=True)


@WOODStream.on_message(filters.command("broadcast") & filters.private & filters.user(Telegram.OWNER_ID) & filters.reply)
async def broadcast_(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text=f"ʙʀᴏᴀᴅᴄᴀsᴛ ɪɴɪᴛɪᴀᴛᴇᴅ ! ʏᴏᴜ ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡɪᴛʜ ʟᴏɢ ғɪʟᴇ ᴡʜᴇɴ ᴀʟʟ ᴛʜᴇ ᴜsᴇʀs ᴀʀᴇ ɴᴏᴛɪғɪᴇᴅ."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id=int(user['id']),
                message=broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current=done,
                        failed=failed,
                        success=success
                    )
                )
                try:
                    await out.edit_text(f"ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀᴛᴜs\n\nᴄᴜʀʀᴇɴᴛ : {done}\nғᴀɪʟᴇᴅ : {failed}\nsᴜᴄᴄᴇss : {success}")
                except:
                    pass
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ `{completed_in}`\n\nᴛᴏᴛᴀʟ ᴜsᴇʀs : {total_users}\nᴛᴏᴛᴀʟ ᴅᴏɴᴇ : {done}\n{success} sᴜᴄᴄᴇss ᴀɴᴅ {failed} ғᴀɪʟᴇᴅ.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ `{completed_in}`\n\nᴛᴏᴛᴀʟ ᴜsᴇʀs : {total_users}\nᴛᴏᴛᴀʟ ᴅᴏɴᴇ : {done}\n{success} sᴜᴄᴄᴇss ᴀɴᴅ {failed} ғᴀɪʟᴇᴅ.",
            quote=True
        )
    os.remove('broadcast.txt')


@WOODStream.on_message(filters.command("del") & filters.private & filters.user(Telegram.OWNER_ID))
async def sts(c: Client, m: Message):
    file_id = m.text.split(" ")[-1]
    try:
        file_info = await db.get_file(file_id)
    except FIleNotFound:
        await m.reply_text(
            text=f"**ғɪʟᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴇʟᴇᴛᴇᴅ**",
            quote=True
        )
        return
    await db.delete_one_file(file_info['_id'])
    await db.count_links(file_info['user_id'], "-")
    await m.reply_text(
        text=f"**ғɪʟᴇ ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ !** ",
        quote=True
    )



