from pathlib import Path

from app.database import init_db
from app.database.session import normalize_database_url


MIGRATIONS_ROOT = Path(__file__).resolve().parents[1] / "migrations"


def test_postgres_migrations_do_not_use_sqlite_datetime_type() -> None:
    postgres_migrations = list((MIGRATIONS_ROOT / "postgres").glob("*.sql"))

    assert postgres_migrations
    for path in postgres_migrations:
        content = path.read_text(encoding="utf-8").upper()
        assert "DATETIME" not in content


def test_postgres_migrations_do_not_contain_dangerous_drop() -> None:
    postgres_migrations = list((MIGRATIONS_ROOT / "postgres").glob("*.sql"))

    assert postgres_migrations
    for path in postgres_migrations:
        content = path.read_text(encoding="utf-8").upper()
        assert "DROP TABLE" not in content
        assert "DROP COLUMN" not in content
        assert "DROP DATABASE" not in content


def test_sqlite_preparation_migration_remains_separated() -> None:
    sqlite_path = MIGRATIONS_ROOT / "sqlite" / "2026_07_02_postgres_preparacao.sql"
    postgres_path = MIGRATIONS_ROOT / "postgres" / "2026_07_02_postgres_preparacao.sql"

    assert sqlite_path.exists()
    assert postgres_path.exists()
    assert "DATETIME" in sqlite_path.read_text(encoding="utf-8").upper()
    assert "TIMESTAMPTZ" in postgres_path.read_text(encoding="utf-8").upper()


def test_postgres_bootstrap_migration_is_first_for_empty_schema() -> None:
    from scripts.apply_postgres_migrations import load_postgres_migrations

    postgres_migrations = load_postgres_migrations()

    assert postgres_migrations[0].name == "2026_07_01_000_postgres_bootstrap_schema.sql"


def test_postgres_backend_only_permissions_runs_after_readiness() -> None:
    from scripts.apply_postgres_migrations import load_postgres_migrations

    names = [path.name for path in load_postgres_migrations()]

    assert names.index("2026_07_12_real_data_readiness.sql") < names.index(
        "2026_07_12_backend_only_permissions.sql"
    )


def test_postgres_official_migration_chain_includes_admin_and_readiness_metadata() -> None:
    from scripts.apply_postgres_migrations import load_postgres_migrations

    names = [path.name for path in load_postgres_migrations()]

    assert names.index("2026_07_12_backend_only_permissions.sql") < names.index(
        "2026_07_15_first_admin_bootstrap.sql"
    )
    assert names.index("2026_07_15_first_admin_bootstrap.sql") < names.index(
        "2026_07_18_production_readiness_metadata.sql"
    )


def test_postgres_bootstrap_creates_base_tables_used_by_later_migrations() -> None:
    bootstrap = MIGRATIONS_ROOT / "postgres" / "2026_07_01_000_postgres_bootstrap_schema.sql"
    content = bootstrap.read_text(encoding="utf-8").lower()

    for table in (
        "leads",
        "clientes",
        "propostas",
        "tarefas",
        "whatsapp_messages",
        "users",
        "audit_logs",
        "consents",
        "simulations",
    ):
        assert f"create table if not exists {table}" in content


def test_production_postgres_does_not_auto_bootstrap_schema(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setattr(init_db, "DATABASE_URL", "postgresql+psycopg://usuario:senha@host:5432/bbb")

    assert init_db.should_auto_bootstrap_schema() is False


def test_sqlite_still_auto_bootstraps_local_controlled_schema(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setattr(init_db, "DATABASE_URL", "sqlite:///./app.db")

    assert init_db.should_auto_bootstrap_schema() is True


def test_sqlite_does_not_auto_bootstrap_in_production_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setattr(init_db, "DATABASE_URL", "sqlite:///./app.db")

    assert init_db.should_auto_bootstrap_schema() is False


def test_postgres_database_url_uses_psycopg_and_requires_ssl() -> None:
    normalized = normalize_database_url("postgres://user:password@db.example.test:5432/app")

    assert normalized.startswith("postgresql+psycopg://")
    assert "sslmode=require" in normalized
