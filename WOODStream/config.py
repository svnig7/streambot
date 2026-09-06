from os import environ as env
from shutil import which
from dotenv import load_dotenv

load_dotenv()

class Telegram:
    API_ID = int(env.get("API_ID"))
    API_HASH = str(env.get("API_HASH"))
    BOT_TOKEN = str(env.get("BOT_TOKEN"))
    OWNER_ID = int(env.get('OWNER_ID', '1234567'))
    WORKERS = int(env.get("WORKERS", "6"))  # 6 workers = 6 commands at once
    DATABASE_URL = str(env.get('DATABASE_URL'))
    UPDATES_CHANNEL = str(env.get('UPDATES_CHANNEL', "bots_7_bots"))
    UPDATES_GROUP = str(env.get('UPDATES_GROUP', "bots_7_bots_support"))
    SESSION_NAME = str(env.get('SESSION_NAME', 'streambot'))
    FORCE_SUB_ID = env.get('FORCE_SUB_ID', None)
    FORCE_SUB_LINK = str(env.get('FORCE_SUB_LINK', 'https://t.me/bots_7_bots'))
    FORCE_SUB_GROUP_ID = env.get('FORCE_SUB_GROUP_ID', None)
    FORCE_SUB_GROUP_LINK = str(env.get('FORCE_SUB_GROUP_LINK', 'https://t.me/rqstgrp7'))
    FORCE_SUB = env.get('FORCE_UPDATES_CHANNEL', True)
    FORCE_SUB = True if str(FORCE_SUB).lower() == "true" else False
    SLEEP_THRESHOLD = int(env.get("SLEEP_THRESHOLD", "60"))
    FILE_PIC = env.get('FILE_PIC', "https://raw.githubusercontent.com/svnig7/images/refs/heads/main/streambotl.png")
    START_PIC = env.get('START_PIC', "https://raw.githubusercontent.com/svnig7/images/refs/heads/main/streambotl.png")
    VERIFY_PIC = env.get('VERIFY_PIC', "https://raw.githubusercontent.com/svnig7/images/refs/heads/main/streambotl.png")
    MULTI_CLIENT = False
    FLOG_CHANNEL = int(env.get("FLOG_CHANNEL", None))   # Logs channel for file logs
    ULOG_CHANNEL = int(env.get("ULOG_CHANNEL", None))   # Logs channel for user logs
    MODE = env.get("MODE", "primary")
    SECONDARY = True if MODE.lower() == "secondary" else False
    AUTH_USERS = list(set(int(x) for x in str(env.get("AUTH_USERS", "")).split()))

    # --- Playlists / TTL links (merged in from telestream-bot) ---
    # Maximum number of items accepted into a single playlist minted from an album.
    MAX_PLAYLIST_ITEMS = int(env.get("MAX_PLAYLIST_ITEMS", "50"))
    # How often (seconds) the background task sweeps expired (TTL) links/playlists.
    CLEANUP_INTERVAL = int(env.get("CLEANUP_INTERVAL", "600"))

class Server:
    PORT = int(env.get("PORT", 8080))
    BIND_ADDRESS = str(env.get("BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(env.get("PING_INTERVAL", "1200"))
    HAS_SSL = str(env.get("HAS_SSL", "0").lower()) in ("1", "true", "t", "yes", "y")
    NO_PORT = str(env.get("NO_PORT", "0").lower()) in ("1", "true", "t", "yes", "y")
    FQDN = str(env.get("FQDN", BIND_ADDRESS))
    URL = "https://{}/".format(FQDN)

    # --- Enhanced web player (merged in from telestream-bot) ---
    # Both default to on but silently turn off if the binaries aren't installed,
    # same behaviour telestream-bot had.
    ENABLE_SUBTITLES = str(env.get("ENABLE_SUBTITLES", "true")).lower() in ("1", "true", "t", "yes", "y") and which("ffmpeg") is not None
    ENABLE_TRACK_PROBE = str(env.get("ENABLE_TRACK_PROBE", "true")).lower() in ("1", "true", "t", "yes", "y") and which("ffprobe") is not None

    # URL of any image to use as the favicon on the web pages (/watch, /xstrm,
    # /playlist). Leave unset for no favicon.
    FAVICON_URL = env.get("FAVICON_URL", "")
