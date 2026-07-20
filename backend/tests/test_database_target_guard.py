import subprocess
import sys
from pathlib import Path

import pytest

from app.services.database_target_guard import (
    APPROVED_MESSAGE,
    DIVERGENT_MESSAGE,
    DatabaseTargetGuardError,
    calculate_database_target_fingerprint,
    guard_if_required,
    validate_database_target,
)

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "database_target_guard.py"
OFFICIAL_URL = "postgresql://backend_app:secret@official.supabase.co:5432/postgres?sslmode=require"


def test_validates_matching_fingerprint_without_printing_target() -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)

    validate_database_target(OFFICIAL_URL, fingerprint)


def test_rejects_other_project_host() -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)

    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        validate_database_target("postgresql://backend_app:secret@other.supabase.co:5432/postgres?sslmode=require", fingerprint)


def test_rejects_other_branch_or_pool_host() -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)

    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        validate_database_target("postgresql://backend_app:secret@branch.pooler.supabase.co:6543/postgres?sslmode=require", fingerprint)


def test_rejects_other_database_name() -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)

    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        validate_database_target("postgresql://backend_app:secret@official.supabase.co:5432/other?sslmode=require", fingerprint)


def test_rejects_missing_fingerprint() -> None:
    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        validate_database_target(OFFICIAL_URL, "")


def test_rejects_invalid_fingerprint() -> None:
    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        validate_database_target(OFFICIAL_URL, "not-a-valid-fingerprint")


def test_rejects_disabled_sslmode() -> None:
    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        calculate_database_target_fingerprint("postgresql://backend_app:secret@official.supabase.co:5432/postgres?sslmode=disable")


def test_rejects_sqlite_target() -> None:
    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        calculate_database_target_fingerprint("sqlite:///./app.db")


def test_guard_if_required_is_noop_without_required_flag() -> None:
    guard_if_required("sqlite:///./app.db", {})


def test_guard_if_required_blocks_when_required_and_fingerprint_missing() -> None:
    with pytest.raises(DatabaseTargetGuardError, match=DIVERGENT_MESSAGE):
        guard_if_required(OFFICIAL_URL, {"DATABASE_TARGET_GUARD_REQUIRED": "true"})


def test_cli_validate_outputs_only_safe_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)
    monkeypatch.setenv("DIRECT_URL", OFFICIAL_URL)
    monkeypatch.setenv("EXPECTED_DATABASE_TARGET_FINGERPRINT", fingerprint)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "validate", "--url-env", "DIRECT_URL"],
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 0
    assert APPROVED_MESSAGE in output
    assert OFFICIAL_URL not in output
    assert "official.supabase.co" not in output
    assert "secret" not in output


def test_cli_validate_failure_outputs_only_safe_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fingerprint = calculate_database_target_fingerprint(OFFICIAL_URL)
    monkeypatch.setenv("DIRECT_URL", "postgresql://backend_app:secret@other.supabase.co:5432/postgres?sslmode=require")
    monkeypatch.setenv("EXPECTED_DATABASE_TARGET_FINGERPRINT", fingerprint)

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "validate", "--url-env", "DIRECT_URL"],
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode == 1
    assert DIVERGENT_MESSAGE in output
    assert "other.supabase.co" not in output
    assert "secret" not in output
