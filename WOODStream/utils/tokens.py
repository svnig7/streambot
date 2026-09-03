import re
from secrets import token_urlsafe

_TOKEN_OK = re.compile(r"^[A-Za-z0-9_-]{4,32}$")
_DURATION = re.compile(r"(\d+)\s*([dhms])", re.I)


def parse_duration(text: str) -> int:
    """'1d2h3m' -> seconds. Returns 0 if unparseable. (ported from telestream-bot)"""
    if not text:
        return 0
    total = 0
    mult = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    for value, unit in _DURATION.findall(text):
        total += int(value) * mult[unit.lower()]
    return total


def new_token() -> str:
    """Short URL-safe opaque id, used for playlist tokens.

    (Individual file links keep using the Mongo ObjectId like streambot
    always did -- this is only for the new playlist collection, which has
    no natural id of its own.)
    """
    return token_urlsafe(5)


def is_valid_token(value: str) -> bool:
    return bool(value) and bool(_TOKEN_OK.match(value))
