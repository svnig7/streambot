import time
import math
import logging
import mimetypes
import traceback
from asyncio import CancelledError, create_subprocess_exec, ensure_future, wait_for
from json import loads as json_loads
from pathlib import Path
from subprocess import PIPE
from urllib.parse import quote

from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine

from WOODStream.bot import multi_clients, work_loads, WOODStream
from WOODStream.config import Telegram, Server
from WOODStream.server.exceptions import FIleNotFound, InvalidHash
from WOODStream import utils, StartTime, __version__
from WOODStream.utils.render_template import render_page
from WOODStream.utils.database import Database

db = Database(Telegram.DATABASE_URL, Telegram.SESSION_NAME)

routes = web.RouteTableDef()

# The two web/*.html pages ported over from telestream-bot for the enhanced
# (multi-audio/subtitle track) player and the playlist viewer.
WEB_DIR = Path(__file__).resolve().parent.parent / "template"


@routes.get("/status", allow_head=True)
async def root_route_handler(_):
    return web.json_response(
        {
            "server_status": "running",
            "uptime": utils.get_readable_time(time.time() - StartTime),
            "telegram_bot": "@" + WOODStream.username,
            "connected_bots": len(multi_clients),
            "loads": dict(
                ("bot" + str(c + 1), l)
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True)
                )
            ),
            "version": __version__,
        }
    )

@routes.get("/watch/{path}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        # Video/audio now always uses the enhanced /xstrm player -
        # opleechplay.html was removed, so a plain-old /watch link for a
        # playable file just forwards there instead of 404ing.
        try:
            file_info = await db.get_file(path)
        except FIleNotFound as e:
            raise web.HTTPNotFound(text=e.message)
        if _playable(file_info.get("mime_type", "")):
            raise web.HTTPFound(f"/xstrm/{path}")
        return web.Response(text=await render_page(path), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass


@routes.get("/dl/{path}", allow_head=True)
async def dl_handler(request: web.Request):
    return await _media_response(request, request.match_info["path"], inline=False)


@routes.get("/stream/{path}", allow_head=True)
async def inline_stream_handler(request: web.Request):
    """Inline (Content-Disposition: inline) counterpart of /dl, used as the
    <video>/<audio> src by the enhanced player page. Merged in from
    telestream-bot, adapted to streambot's ByteStreamer."""
    return await _media_response(request, request.match_info["path"], inline=True)


async def _media_response(request: web.Request, path: str, inline: bool):
    try:
        return await media_streamer(request, path, inline=inline)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        traceback.print_exc()
        logging.critical(e.with_traceback(None))
        logging.debug(traceback.format_exc())
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}


def _pick_client():
    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]
    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
    else:
        tg_connect = utils.ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    return index, tg_connect


def _byte_range(tg_connect, file_id, index, from_bytes, until_bytes, file_size):
    """Same offset/part-count math the original media_streamer used, factored
    out so track-probing and subtitle extraction can reuse it."""
    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )
    return body, req_length


async def media_streamer(request: web.Request, db_id: str, inline: bool = False):
    range_header = request.headers.get("Range", 0)

    index, tg_connect = _pick_client()

    if Telegram.MULTI_CLIENT:
        logging.info(f"Client {index} is now serving {request.headers.get('X-FORWARDED-FOR',request.remote)}")

    file_id = await tg_connect.get_file_properties(db_id, multi_clients)

    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    body, req_length = _byte_range(tg_connect, file_id, index, from_bytes, until_bytes, file_size)
    until_bytes = min(until_bytes, file_size - 1)

    mime_type = file_id.mime_type
    file_name = utils.get_name(file_id)
    disposition = "inline" if inline else "attachment"

    if not mime_type:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )

@routes.get("/file/{_id}")
async def file_deeplink(request: web.Request):
    _id = request.match_info["_id"]
    raise web.HTTPFound(f"https://t.me/{WOODStream.username}?start=file_{_id}")


# ============================================================================
# Everything below is merged in from telestream-bot: the enhanced player page
# (multi-audio/subtitle track switching), playlists, and TTL-aware metadata.
# The frontend (web/stream.html, web/playlist.html) is used verbatim - only
# the backend routes it talks to are reimplemented here against streambot's
# Mongo `file`/`playlist` collections instead of telestream's `streams` one.
# ============================================================================

def _playable(mime_type: str) -> bool:
    return bool(mime_type) and (mime_type.startswith("video") or mime_type.startswith("audio"))


@routes.get("/xstrm/{path}", allow_head=True)
async def enhanced_player_page(request: web.Request):
    return await _serve_with_bot_link(WEB_DIR / "watch.html")


@routes.get("/playlist/{path}", allow_head=True)
async def playlist_page(request: web.Request):
    return await _serve_with_bot_link(WEB_DIR / "playlist.html")


_page_cache = {}


async def _serve_with_bot_link(path: Path):
    """watch.html/playlist.html are static files, but the topbar title and
    footer Telegram icon need the bot's own @username link baked in -
    swapped in for the __BOT_LINK__ placeholder at request time rather than
    re-reading + re-templating the (large) file on every request."""
    bot_link = f"https://t.me/{WOODStream.username}"
    cached = _page_cache.get(path)
    if not cached:
        cached = path.read_text(encoding="utf-8")
        _page_cache[path] = cached
    return web.Response(text=cached.replace("__BOT_LINK__", bot_link), content_type="text/html")


async def _playlist_nav(file_info):
    """prev/next info for a file that's part of a playlist, in the same
    shape web/stream.html expects."""
    token = file_info.get("pl")
    if not token:
        return None
    doc = await db.get_playlist(token)
    if not doc:
        return None
    items = doc["items"]
    if not items:
        return None
    idx = file_info.get("pi", 0)
    out = {
        "token": token,
        "name": doc.get("name") or "Playlist",
        "index": idx + 1,
        "total": len(items),
        "prev": None,
        "next": None,
    }
    for key, at in (("prev", idx - 1), ("next", idx + 1)):
        if at < 0 or at >= len(items):
            continue
        try:
            neighbour = await db.get_file(items[at])
        except FIleNotFound:
            continue
        out[key] = {"token": items[at], "name": neighbour.get("file_name") or "Untitled"}
    return out


@routes.get("/api/stream/{path}")
async def api_meta(request: web.Request):
    db_id = request.match_info["path"]
    try:
        file_info = await db.get_file(db_id)
    except FIleNotFound:
        raise web.HTTPNotFound(text="unknown link")
    body = {
        "name": file_info.get("file_name") or "File",
        "size": int(file_info.get("file_size") or 0),
        "mime": file_info.get("mime_type") or "application/octet-stream",
        "unique_id": file_info.get("file_unique_id") or db_id,
        "playable": _playable(file_info.get("mime_type", "")),
    }
    nav = await _playlist_nav(file_info)
    if nav:
        body["playlist"] = nav
    return web.json_response(body)


@routes.get("/poster/{path}")
async def poster_handler(request: web.Request):
    """Custom cover art (set via /poster) - just a redirect to the stored
    URL. If this file has no poster but belongs to a playlist, fall back to
    the playlist's poster."""
    db_id = request.match_info["path"]
    try:
        file_info = await db.get_file(db_id)
    except FIleNotFound:
        raise web.HTTPNotFound(text="unknown link")

    poster = file_info.get("poster")
    if not poster and file_info.get("pl"):
        pl_doc = await db.get_playlist(file_info["pl"])
        if pl_doc:
            poster = pl_doc.get("poster")
    if not poster:
        raise web.HTTPNotFound(text="no artwork")
    raise web.HTTPFound(poster)


_PROBE_BYTES = 6 * 1024 * 1024
_PROBE_TIMEOUT = 45
_probe_cache = {}
_PROBE_CACHE_KEEP = 128


async def _prefix_bytes(tg_connect, file_id, index, n, file_size):
    n = min(n, file_size)
    body, _ = _byte_range(tg_connect, file_id, index, 0, n - 1, file_size)
    buf = bytearray()
    try:
        async for chunk in body:
            buf.extend(chunk)
            if len(buf) >= n:
                break
    finally:
        # yield_file() only decrements work_loads[index] in its own finally
        # block, which only runs once the generator is exhausted/closed - if
        # we stop consuming early (as we always do here) we must close it
        # ourselves or that client looks permanently busier than it is.
        await body.aclose()
    return bytes(buf[:n])


async def _probe_tracks(db_id, tg_connect, index, file_id):
    if not Server.ENABLE_TRACK_PROBE:
        return {"audio": [], "subtitle": []}
    if db_id in _probe_cache:
        return _probe_cache[db_id]

    raw = await _prefix_bytes(tg_connect, file_id, index, _PROBE_BYTES, file_id.file_size)
    try:
        proc = await create_subprocess_exec(
            "ffprobe", "-hide_banner", "-loglevel", "error",
            "-print_format", "json", "-show_streams", "-",
            stdin=PIPE, stdout=PIPE, stderr=PIPE,
        )
        out, _ = await wait_for(proc.communicate(raw), timeout=_PROBE_TIMEOUT)
        streams = json_loads(out).get("streams", [])
    except Exception as e:
        logging.debug(f"ffprobe failed for {db_id}: {e}")
        streams = []

    audio, subtitle = [], []
    for st in streams:
        kind = st.get("codec_type")
        tags = st.get("tags") or {}
        label = tags.get("title") or tags.get("language") or ""
        if kind == "audio":
            audio.append({"index": len(audio), "title": label or f"Track {len(audio) + 1}", "codec": st.get("codec_name", "")})
        elif kind == "subtitle" and (st.get("codec_name") or "") not in ("dvd_subtitle", "hdmv_pgs_subtitle", "dvb_subtitle"):
            subtitle.append({"index": len(subtitle), "title": label or f"Track {len(subtitle) + 1}"})

    result = {"audio": audio, "subtitle": subtitle}
    _probe_cache[db_id] = result
    if len(_probe_cache) > _PROBE_CACHE_KEEP:
        _probe_cache.pop(next(iter(_probe_cache)))
    return result


@routes.get("/api/tracks/{path}")
async def api_tracks(request: web.Request):
    db_id = request.match_info["path"]
    try:
        await db.get_file(db_id)
    except FIleNotFound:
        raise web.HTTPNotFound(text="unknown link")
    index, tg_connect = _pick_client()
    file_id = await tg_connect.get_file_properties(db_id, multi_clients)
    return web.json_response(await _probe_tracks(db_id, tg_connect, index, file_id))


@routes.get("/subs/{path}/{idx}")
async def subs_handler(request: web.Request):
    if not Server.ENABLE_SUBTITLES:
        raise web.HTTPServiceUnavailable(text="subtitle extraction is disabled on this deployment")

    db_id = request.match_info["path"]
    raw_idx = request.match_info["idx"]
    if raw_idx.endswith(".vtt"):
        raw_idx = raw_idx[:-4]
    try:
        idx = int(raw_idx)
    except ValueError:
        raise web.HTTPNotFound(text="bad track") from None
    if idx < 0 or idx > 31:
        raise web.HTTPNotFound(text="bad track")

    try:
        await db.get_file(db_id)
    except FIleNotFound:
        raise web.HTTPNotFound(text="unknown link")

    index, tg_connect = _pick_client()
    file_id = await tg_connect.get_file_properties(db_id, multi_clients)
    body, _ = _byte_range(tg_connect, file_id, index, 0, file_id.file_size - 1, file_id.file_size)

    proc = await create_subprocess_exec(
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-threads", "1",
        "-vn", "-an", "-i", "pipe:0", "-map", f"0:s:{idx}",
        "-f", "webvtt", "-flush_packets", "1", "pipe:1",
        stdin=PIPE, stdout=PIPE, stderr=PIPE,
    )

    resp = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/vtt; charset=utf-8",
            "Cache-Control": "private, max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )
    await resp.prepare(request)

    async def feed():
        try:
            async for piece in body:
                proc.stdin.write(piece)
                await proc.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            try:
                await body.aclose()
            except Exception:
                pass
            try:
                proc.stdin.close()
            except Exception:
                pass

    pusher = ensure_future(feed())
    try:
        while True:
            chunk = await proc.stdout.read(65536)
            if not chunk:
                break
            await resp.write(chunk)
        await resp.write_eof()
    except (ConnectionResetError, ConnectionError, CancelledError):
        pass
    finally:
        pusher.cancel()
        try:
            proc.kill()
        except Exception:
            pass
    return resp


@routes.get("/api/playlist/{path}")
async def api_playlist(request: web.Request):
    token = request.match_info["path"]
    doc = await db.get_playlist(token)
    if not doc:
        raise web.HTTPNotFound(text="unknown link")

    items = []
    for db_id in doc["items"]:
        try:
            file_info = await db.get_file(db_id)
        except FIleNotFound:
            continue
        items.append({
            "token": db_id,
            "name": file_info.get("file_name") or "Untitled",
            "size": int(file_info.get("file_size") or 0),
            "mime": file_info.get("mime_type") or "application/octet-stream",
            "playable": _playable(file_info.get("mime_type", "")),
        })

    body = {"name": doc.get("name") or (items[0]["name"] if items else "Playlist"), "items": items}
    return web.json_response(body)
