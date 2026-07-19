from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.services.datetime_utc import is_expired, utc_from_internal, utc_now


def test_utc_now_returns_aware_utc_datetime() -> None:
    now = utc_now()

    assert now.tzinfo is UTC
    assert now.utcoffset() == timedelta(0)


def test_utc_from_internal_accepts_aware_utc() -> None:
    value = datetime(2026, 7, 19, 12, 0, tzinfo=UTC)

    assert utc_from_internal(value) == value


def test_utc_from_internal_converts_other_offset_to_utc() -> None:
    value = datetime(2026, 7, 19, 9, 0, tzinfo=timezone(timedelta(hours=-3)))

    assert utc_from_internal(value) == datetime(2026, 7, 19, 12, 0, tzinfo=UTC)


def test_utc_from_internal_treats_internal_naive_datetime_as_utc() -> None:
    value = datetime(2026, 7, 19, 12, 0)

    assert utc_from_internal(value) == datetime(2026, 7, 19, 12, 0, tzinfo=UTC)


def test_utc_from_internal_rejects_missing_or_invalid_values() -> None:
    with pytest.raises(ValueError):
        utc_from_internal(None)
    with pytest.raises(ValueError):
        utc_from_internal("2026-07-19T12:00:00Z")  # type: ignore[arg-type]


def test_is_expired_uses_less_or_equal_boundary() -> None:
    now = datetime(2026, 7, 19, 12, 0, tzinfo=UTC)

    assert is_expired(now + timedelta(seconds=1), now) is False
    assert is_expired(now - timedelta(seconds=1), now) is True
    assert is_expired(now, now) is True


def test_is_expired_has_no_naive_aware_type_error() -> None:
    naive_internal = datetime(2026, 7, 19, 12, 0)
    aware_now = datetime(2026, 7, 19, 12, 0, tzinfo=UTC)

    assert is_expired(naive_internal, aware_now) is True
