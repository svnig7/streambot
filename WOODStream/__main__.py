import sys
import asyncio
import logging
import traceback
import logging.handlers as handlers
from WOODStream.config import Telegram, Server
from aiohttp import web
from pyrogram import idle

from WOODStream.bot import WOODStream
from WOODStream.server import web_server
from WOODStream.bot.clients import initialize_clients
from WOODStream.utils.database import Database

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout),
              handlers.RotatingFileHandler("streambot.log", mode="a", maxBytes=104857600, backupCount=2, encoding="utf-8")],)

logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

server = web.AppRunner(web_server())

loop = asyncio.get_event_loop()

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)


async def ttl_cleanup_loop():
    """Periodically sweeps expired TTL links/playlists (feature merged in
    from telestream-bot). Runs forever until the process exits."""
    while True:
        await asyncio.sleep(Telegram.CLEANUP_INTERVAL)
        try:
            files, playlists = await db.purge_expired()
            if files or playlists:
                logging.info(f"TTL sweep: removed {files} expired file(s), {playlists} expired playlist(s)")
        except Exception:
            logging.error(traceback.format_exc())


async def start_services():
    print()
    if Telegram.SECONDARY:
        print("------------------ Starting as Secondary Server ------------------")
    else:
        print("------------------- Starting as Primary Server -------------------")
    print()
    print("-------------------- Initializing Telegram Bot --------------------")


    await WOODStream.start()
    bot_info = await WOODStream.get_me()
    WOODStream.id = bot_info.id
    WOODStream.username = bot_info.username
    WOODStream.fname=bot_info.first_name
    print("------------------------------ DONE ------------------------------")
    print()
    print("---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    print("------------------------------ DONE ------------------------------")
    print()
    print("--------------------- Initializing Database ------------------------")
    await db.ensure_indexes()
    asyncio.create_task(ttl_cleanup_loop())
    print("------------------------------ DONE ------------------------------")
    print()
    print("--------------------- Initializing Web Server ---------------------")
    await server.setup()
    await web.TCPSite(server, Server.BIND_ADDRESS, Server.PORT).start()
    print("------------------------------ DONE ------------------------------")
    print()
    print("------------------------- Service Started -------------------------")
    print("                        bot =>> {}".format(bot_info.first_name))
    if bot_info.dc_id:
        print("                        DC ID =>> {}".format(str(bot_info.dc_id)))
    print(" URL =>> {}".format(Server.URL))
    print("------------------------------------------------------------------")
    await idle()

async def cleanup():
    await server.cleanup()
    await WOODStream.stop()

if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(traceback.format_exc())
    finally:
        loop.run_until_complete(cleanup())
        loop.stop()
        print("------------------------ Stopped Services ------------------------")