from pathlib import Path

import pytest

from app.services.test_database_guard import TestDatabaseGuardError, guard_test_database_url


def _env(run_id: str = "pytest-guard-1234") -> dict[str, str]:
    return {
        "APP_ENV": "test",
        "BBB_TEST_RUN_ID": run_id,
    }


def test_guard_rejects_supabase_target() -> None:
    with pytest.raises(TestDatabaseGuardError, match="bloqueado"):
        guard_test_database_url(
            "postgresql+psycopg://user:pass@db.example.supabase.co:5432/postgres?sslmode=require",
            _env(),
        )


def test_guard_rejects_render_target() -> None:
    with pytest.raises(TestDatabaseGuardError, match="bloqueado"):
        guard_test_database_url("postgresql+psycopg://user:pass@crm-2340.onrender.com:5432/crm_test", _env())


def test_guard_rejects_workspace_sqlite_database() -> None:
    workspace_db = Path(__file__).resolve().parents[1] / "app.db"
    with pytest.raises(TestDatabaseGuardError, match="persistente"):
        guard_test_database_url(f"sqlite:///{workspace_db.as_posix()}", _env())


def test_guard_rejects_missing_test_run_id() -> None:
    with pytest.raises(TestDatabaseGuardError, match="identificador"):
        guard_test_database_url("sqlite:////tmp/pytest-safe.sqlite", {"APP_ENV": "test"})


def test_guard_allows_explicit_temporary_sqlite(tmp_path: Path) -> None:
    run_id = "pytest-safe-1234"
    database = tmp_path / run_id / "db.sqlite"
    database.parent.mkdir()
    guard_test_database_url(f"sqlite:///{database.as_posix()}", _env(run_id))


def test_guard_allows_disposable_local_postgres() -> None:
    guard_test_database_url(
        "postgresql+psycopg://postgres:test@127.0.0.1:5432/crm_test_pytest_1234?sslmode=disable",
        _env("pytest-1234"),
    )


@pytest.mark.parametrize("key", ["SUPABASE_DIRECT_URL", "DIRECT_URL", "POSTGRES_RESTORE_URL"])
def test_guard_rejects_production_database_secret_env(key: str) -> None:
    env = _env()
    env[key] = "postgresql://hidden@localhost/crm_test"
    with pytest.raises(TestDatabaseGuardError, match=key):
        guard_test_database_url("sqlite:////tmp/pytest-guard-1234/db.sqlite", env)
