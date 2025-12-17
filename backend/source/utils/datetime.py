import datetime


def ensure_utc(dt: datetime.datetime) -> datetime.datetime:
    """
    Ensure a datetime is timezone-aware and converted to UTC.

    If the datetime is naive (no timezone info), it's assumed to be UTC.
    If it has timezone info, it's converted to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.UTC)
    return dt.astimezone(datetime.UTC)
