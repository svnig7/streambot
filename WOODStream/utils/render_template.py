import aiohttp
import jinja2
import urllib.parse
from WOODStream.bot import WOODStream
from WOODStream.config import Telegram, Server
from WOODStream.utils.database import Database
from WOODStream.utils.human_readable import humanbytes
db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

async def render_page(db_id):
    file_data=await db.get_file(db_id)
    src = urllib.parse.urljoin(Server.URL, f'dl/{file_data["_id"]}')
    file_size = humanbytes(file_data['file_size'])
    file_name = file_data['file_name'].replace("_", " ")
    bot_link = f"https://t.me/{WOODStream.username}"
    favicon_url = Server.FAVICON_URL or "data:,"

    # Video/audio is served by the enhanced /xstrm player instead (see
    # stream_routes.stream_handler, which redirects there before this ever
    # runs) - opleechplay.html has been removed, this now only ever renders
    # the plain download page.
    template_file = "WOODStream/template/dl.html"
    async with aiohttp.ClientSession() as s:
        async with s.get(src) as u:
            file_size = humanbytes(int(u.headers.get('Content-Length')))

    with open(template_file) as f:
        template = jinja2.Template(f.read(), autoescape=True)

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        bot_link=bot_link,
        favicon_url=favicon_url
    )
