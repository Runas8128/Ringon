from datetime import datetime, timedelta, timezone

__all__ = (
    'now'
)

def now() -> datetime:
    return datetime.now(tz=timezone(offset=timedelta(hours=9)))
