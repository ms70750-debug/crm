from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from scripts import apply_single_postgres_migration as single


def _write_allowed_migrations(root: Path) -> None:
    (root / "2026_07_01_000_postgres_bootstrap_schema.sql").write_text(
        """
        CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS propostas (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS tarefas (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS whatsapp_messages (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS consents (id INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS simulations (id INTEGER PRIMARY KEY);
        """,
        encoding="utf-8",
    )
    (root / "2026_07_02_postgres_preparacao.sql").write_text(
        "ALTER TABLE leads ADD COLUMN created_at TEXT;",
        encoding="utf-8",
    )
    (root / "2026_07_12_auth_sessions.sql").write_text(
        "CREATE TABLE IF NOT EXISTS auth_sessions (id INTEGER PRIMARY KEY, session_id_hash TEXT);",
        encoding="utf-8",
    )
    (root / "2026_07_12_real_data_readiness.sql").write_text(
        "CREATE TABLE IF NOT EXISTS backup_audit_logs (id INTEGER PRIMARY KEY);",
        encoding="utf-8",
    )
    (root / "2026_07_12_backend_only_permissions.sql").write_text(
        "REVOKE SELECT ON TABLE leads FROM anon;",
        encoding="utf-8",
    )
    (root / "2026_07_15_first_admin_bootstrap.sql").write_text(
        "CREATE TABLE IF NOT EXISTS admin_bootstrap_tokens (id INTEGER PRIMARY KEY, token_hash TEXT);",
        encoding="utf-8",
    )


@pytest.fixture()
def migration_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _write_allowed_migrations(tmp_path)
    monkeypatch.setattr(single, "MIGRATIONS_DIR", tmp_path)
    return tmp_path


def test_single_migration_rejects_invalid_confirmation(migration_dir: Path) -> None:
    with pytest.raises(RuntimeError, match="Confirmacao invalida"):
        single.run_single_migration(
            migration_name="2026_07_01_000_postgres_bootstrap_schema.sql",
            expected_previous=single.NONE_PREVIOUS,
            confirmation="SIM",
            direct_url="sqlite:///:memory:",
        )


def test_single_migration_rejects_invalid_migration_name(migration_dir: Path) -> None:
    with pytest.raises(RuntimeError, match="Migration nao permitida"):
        single.run_single_migration(
            migration_name="2026_07_99_maliciosa.sql",
            expected_previous=single.NONE_PREVIOUS,
            confirmation=single.CONFIRMATION_VALUE,
            direct_url="sqlite:///:memory:",
        )


def test_single_migration_rejects_wrong_order_input(migration_dir: Path) -> None:
    with pytest.raises(RuntimeError, match="Ordem invalida"):
        single.run_single_migration(
            migration_name="2026_07_12_auth_sessions.sql",
            expected_previous=single.NONE_PREVIOUS,
            confirmation=single.CONFIRMATION_VALUE,
            direct_url="sqlite:///:memory:",
        )


def test_single_migration_applies_one_file_and_registers_checksum(migration_dir: Path, tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'single-ok.sqlite').as_posix()}"

    single.run_single_migration(
        migration_name="2026_07_01_000_postgres_bootstrap_schema.sql",
        expected_previous=single.NONE_PREVIOUS,
        confirmation=single.CONFIRMATION_VALUE,
        direct_url=db_url,
    )

    engine = create_engine(db_url)
    with engine.connect() as conn:
        tables = set(conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type = 'table'").scalars())
        applied = conn.execute(text("SELECT version, checksum FROM schema_migrations")).fetchall()

    assert "leads" in tables
    assert "auth_sessions" not in tables
    assert applied[0][0] == "2026_07_01_000_postgres_bootstrap_schema.sql"
    assert len(applied[0][1]) == 64


def test_single_migration_blocks_reapply(migration_dir: Path, tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'single-reapply.sqlite').as_posix()}"
    kwargs = {
        "migration_name": "2026_07_01_000_postgres_bootstrap_schema.sql",
        "expected_previous": single.NONE_PREVIOUS,
        "confirmation": single.CONFIRMATION_VALUE,
        "direct_url": db_url,
    }

    single.run_single_migration(**kwargs)

    with pytest.raises(RuntimeError, match="Reaplicacao bloqueada"):
        single.run_single_migration(**kwargs)


def test_single_migration_can_allow_already_applied_when_objects_exist(migration_dir: Path, tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'single-already-applied.sqlite').as_posix()}"
    kwargs = {
        "migration_name": "2026_07_01_000_postgres_bootstrap_schema.sql",
        "expected_previous": single.NONE_PREVIOUS,
        "confirmation": single.CONFIRMATION_VALUE,
        "direct_url": db_url,
    }

    single.run_single_migration(**kwargs)
    single.run_single_migration(**kwargs, allow_already_applied=True)

    engine = create_engine(db_url)
    with engine.connect() as conn:
        applied = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()

    assert applied == [("2026_07_01_000_postgres_bootstrap_schema.sql",)]


def test_single_migration_blocks_checksum_drift(migration_dir: Path, tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'single-checksum.sqlite').as_posix()}"
    engine = create_engine(db_url)
    with engine.begin() as conn:
        single.ensure_control_table(conn)
        conn.execute(
            text("INSERT INTO schema_migrations (version, checksum) VALUES (:version, :checksum)"),
            {"version": "2026_07_01_000_postgres_bootstrap_schema.sql", "checksum": "0" * 64},
        )

    with pytest.raises(RuntimeError, match="Checksum divergente"):
        single.run_single_migration(
            migration_name="2026_07_02_postgres_preparacao.sql",
            expected_previous="2026_07_01_000_postgres_bootstrap_schema.sql",
            confirmation=single.CONFIRMATION_VALUE,
            direct_url=db_url,
        )


def test_single_migration_blocks_missing_previous(migration_dir: Path, tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'single-order.sqlite').as_posix()}"

    with pytest.raises(RuntimeError, match="migration anterior esperada"):
        single.run_single_migration(
            migration_name="2026_07_02_postgres_preparacao.sql",
            expected_previous="2026_07_01_000_postgres_bootstrap_schema.sql",
            confirmation=single.CONFIRMATION_VALUE,
            direct_url=db_url,
        )


def test_single_migration_allows_backend_only_permissions_after_readiness(migration_dir: Path) -> None:
    assert "2026_07_12_backend_only_permissions.sql" in single.ALLOWED_MIGRATIONS
    assert (
        single.EXPECTED_PREVIOUS["2026_07_12_backend_only_permissions.sql"]
        == "2026_07_12_real_data_readiness.sql"
    )
    assert single.validate_selection(
        "2026_07_12_backend_only_permissions.sql",
        "2026_07_12_real_data_readiness.sql",
    ).name == "2026_07_12_backend_only_permissions.sql"


def test_single_migration_allows_first_admin_after_backend_only_permissions(migration_dir: Path) -> None:
    assert "2026_07_15_first_admin_bootstrap.sql" in single.ALLOWED_MIGRATIONS
    assert (
        single.EXPECTED_PREVIOUS["2026_07_15_first_admin_bootstrap.sql"]
        == "2026_07_12_backend_only_permissions.sql"
    )
    assert single.validate_selection(
        "2026_07_15_first_admin_bootstrap.sql",
        "2026_07_12_backend_only_permissions.sql",
    ).name == "2026_07_15_first_admin_bootstrap.sql"


def test_single_migration_rejects_backend_only_permissions_wrong_order(migration_dir: Path) -> None:
    with pytest.raises(RuntimeError, match="Ordem invalida"):
        single.validate_selection(
            "2026_07_12_backend_only_permissions.sql",
            "2026_07_12_auth_sessions.sql",
        )


def test_single_migration_rolls_back_on_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "2026_07_01_000_postgres_bootstrap_schema.sql").write_text(
        """
        CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY);
        CREATE INDEX ix_missing_table ON tabela_inexistente (id);
        """,
        encoding="utf-8",
    )
    for name in single.ALLOWED_MIGRATIONS[1:]:
        (tmp_path / name).write_text("CREATE TABLE IF NOT EXISTS placeholder (id INTEGER PRIMARY KEY);", encoding="utf-8")
    monkeypatch.setattr(single, "MIGRATIONS_DIR", tmp_path)
    db_url = f"sqlite:///{(tmp_path / 'single-rollback.sqlite').as_posix()}"

    with pytest.raises(Exception):
        single.run_single_migration(
            migration_name="2026_07_01_000_postgres_bootstrap_schema.sql",
            expected_previous=single.NONE_PREVIOUS,
            confirmation=single.CONFIRMATION_VALUE,
            direct_url=db_url,
        )

    engine = create_engine(db_url)
    with engine.connect() as conn:
        applied = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()

    assert applied == []
