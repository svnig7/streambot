from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from WOODStream.config import Telegram

class LANG(object):

    START_TEXT = """
<b>👋 Hey, </b>{}\n 
<b>I'm a Telegram File Stream Bot as well as a Direct Link Generator Bot.</b>\n
<b>Working on channels and private chats.</b>"""

    HELP_TEXT = """
<b>- Add me as an admin on the channel</b>
<b>- Send me any file</b>
<b>- I'll provide a streamable link</b>
<b>- Send a whole album and I'll bundle it into one playlist link</b>
<b>- Reply `/ttl 1d2h` to any link to make it self-expire</b>
<b>- Reply `/poster <url>` to set custom cover art</b>\n
<b>🔞 Adult content strictly prohibited.</b>"""

    ABOUT_TEXT = """
<b>⚜ My Name: {}</b>\n
<b>✦ Version: {}</b>
<b>✦ Owner: <a href='https://t.me/stremio_updates'>❖ Stremio Updates❖ ™</a></b>\n
"""

    STREAM_TEXT = """
<b>File Name:</b> <code>{}</code>
<b>File Size:</b> <code>{}</code>
<b>Stream Link:</b> <code>{}</code>
<b>Download Link:</b> <code>{}</code>
<b>File Link:</b> <code>{}</code>"""

    STREAM_TEXT_X = """
<b>File Name:</b> <code>{}</code>
<b>File Size:</b> <code>{}</code>
<b>Stream Link:</b> <code>{}</code>
<b>Download Link:</b> <code>{}</code>
<b>File Link:</b> <code>{}</code>"""

    BAN_TEXT = "Sorry, you are banned from using me.\n\n**[Contact Dev](tg://user?id={}) - they will help you.**"

class BUTTON(object):
    START_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Update Channel", url=f'https://t.me/{Telegram.UPDATES_CHANNEL}'),
                InlineKeyboardButton("Update Group", url=f'https://t.me/{Telegram.UPDATES_GROUP}'),
            ],
            [
                InlineKeyboardButton('Help', callback_data='help'),
                InlineKeyboardButton('About', callback_data='about'),
            ],
            [InlineKeyboardButton('Close', callback_data='close')],
        ]
    )
    HELP_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('Home', callback_data='home'),
            InlineKeyboardButton('About', callback_data='about'),
        ],
            [InlineKeyboardButton('Close', callback_data='close')]
        ]
    )
    ABOUT_BUTTONS = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('Home', callback_data='home'),
            InlineKeyboardButton('Help', callback_data='help'),
        ],
            [InlineKeyboardButton('Close', callback_data='close')]
        ]
    )
