from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_from_internal(value: datetime | None) -> datetime:
    if value is None or not isinstance(value, datetime):
        raise ValueError("datetime UTC interno invalido")
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def is_expired(expires_at: datetime | None, now: datetime | None = None) -> bool:
    return utc_from_internal(expires_at) <= utc_from_internal(now or utc_now())
