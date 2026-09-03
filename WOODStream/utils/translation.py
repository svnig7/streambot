from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from WOODStream.config import Telegram

class LANG(object):

    START_TEXT = """
<b>👋 ʜᴇʏ, </b>{}\n 
<b>ɪ'ᴍ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇ sᴛʀᴇᴀᴍ ʙᴏᴛ ᴀs ᴡᴇʟʟ ᴀs ᴅɪʀᴇᴄᴛ ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴏʀ ʙᴏᴛ</b>\n
<b>ᴡᴏʀᴋɪɴɢ ᴏɴ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ</b>"""

    HELP_TEXT = """
<b>- ᴀᴅᴅ ᴍᴇ ᴀs ᴀɴ ᴀᴅᴍɪɴ ᴏɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ</b>
<b>- sᴇɴᴅ ᴍᴇ ᴀɴʏ ғɪʟᴇ</b>
<b>- ɪ'ʟʟ ᴘʀᴏᴠɪᴅᴇ sᴛʀᴇᴀᴍᴀʙʟᴇ ʟɪɴᴋ</b>
<b>- sᴇɴᴅ ᴀ ᴡʜᴏʟᴇ ᴀʟʙᴜᴍ ᴀɴᴅ ɪ'ʟʟ ʙᴜɴᴅʟᴇ ɪᴛ ɪɴᴛᴏ ᴏɴᴇ ᴘʟᴀʏʟɪsᴛ ʟɪɴᴋ</b>
<b>- ʀᴇᴘʟʏ `/ttl 1d2h` ᴛᴏ ᴀɴʏ ʟɪɴᴋ ᴛᴏ ᴍᴀᴋᴇ ɪᴛ sᴇʟғ-ᴇxᴘɪʀᴇ</b>
<b>- ʀᴇᴘʟʏ `/poster <url>` ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴄᴏᴠᴇʀ ᴀʀᴛ</b>\n
<b>🔞 ᴀᴅᴜʟᴛ ᴄᴏɴᴛᴇɴᴛ sᴛʀɪᴄᴛʟʏ ᴘʀᴏʜɪʙɪᴛᴇᴅ.</b>"""

    ABOUT_TEXT = """
<b>⚜ ᴍʏ ɴᴀᴍᴇ : {}</b>\n
<b>✦ ᴠᴇʀsɪᴏɴ : {}</b>
<b>✦ ᴏᴡɴᴇʀ : <a href='https://telegram.me/cntct_7bot'>❖ sᴠɴ ❖ ™</a></b>\n
"""

    STREAM_TEXT = """
<b>ғɪʟᴇ ɴᴀᴍᴇ :</b> <code>{}</code>
<b>ғɪʟᴇ sɪᴢᴇ :</b> <code>{}</code>
<b>sᴛʀᴇᴀᴍ ʟɪɴᴋ :</b> <code>{}</code>
<b>ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ :</b> <code>{}</code>
<b>ғɪʟᴇ ʟɪɴᴋ :</b> <code>{}</code>"""

    STREAM_TEXT_X = """
<b>ғɪʟᴇ ɴᴀᴍᴇ :</b> <code>{}</code>
<b>ғɪʟᴇ sɪᴢᴇ :</b> <code>{}</code>
<b>sᴛʀᴇᴀᴍ ʟɪɴᴋ :</b> <code>{}</code>
<b>ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ :</b> <code>{}</code>
<b>ғɪʟᴇ ʟɪɴᴋ :</b> <code>{}</code>"""

    BAN_TEXT = "sᴏʀʀʏ sɪʀ, ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ᴛᴏ ᴜsᴇ ᴍᴇ\n\n**[ ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠ ](tg://user?id={}) ᴛʜᴇʏ ᴡɪʟʟ ʜᴇʟᴘ ʏᴏᴜ**"

class BUTTON(object):
    START_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close')
        ],
            [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/{Telegram.UPDATES_CHANNEL}')]
        ]
    )
    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close'),
        ],
            [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/{Telegram.UPDATES_CHANNEL}')]
        ]
    )
    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='home'),
            InlineKeyboardButton('ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close'),
        ],
            [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/{Telegram.UPDATES_CHANNEL}')]
        ]
    )
