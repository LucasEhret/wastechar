"""Per-account wall-clock time with daylight-saving rules."""

import datetime as dt
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_TIMEZONE = "Europe/Zurich"


def account_timezone(name: str | None) -> ZoneInfo:
    name = name or DEFAULT_TIMEZONE
    try:
        return ZoneInfo(name)
    except (TypeError, ValueError, ZoneInfoNotFoundError):
        raise ValueError(f"Invalid account time zone: {name}") from None


def local_now(name: str | None = None) -> dt.datetime:
    return dt.datetime.now(account_timezone(name))


def local_today(name: str | None = None) -> dt.date:
    return local_now(name).date()


def in_account_timezone(instant: dt.datetime, name: str | None = None) -> dt.datetime:
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Timestamp must include a time zone")
    return instant.astimezone(account_timezone(name))
