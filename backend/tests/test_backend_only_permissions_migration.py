import re
from pathlib import Path

from scripts import apply_postgres_migrations as migrations
from scripts import apply_single_postgres_migration as single

MIGRATIONS_ROOT = Path(__file__).resolve().parents[1] / "migrations" / "postgres"
MIGRATION_PATH = MIGRATIONS_ROOT / "2026_07_12_backend_only_permissions.sql"
ROLLBACK_PATH = MIGRATIONS_ROOT / "rollback" / "2026_07_12_backend_only_permissions_down.sql"
VALIDATION_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_backend_only_permissions.py"
EXPECTED_TABLES = (
    "audit_logs",
    "auth_sessions",
    "backup_audit_logs",
    "clientes",
    "consents",
    "leads",
    "propostas",
    "schema_migrations",
    "simulations",
    "tarefas",
    "users",
    "whatsapp_messages",
)


def _content() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_backend_only_permissions_migration_exists_and_has_rollback() -> None:
    assert MIGRATION_PATH.exists()
    assert ROLLBACK_PATH.exists()


def test_backend_only_permissions_revokes_direct_roles_from_all_expected_tables() -> None:
    content = _content()
    normalized = re.sub(r"\s+", " ", content.lower())

    assert "backend-only" in normalized
    assert "from public, anon, authenticated" in normalized
    for privilege in ("select", "insert", "update", "delete", "truncate", "references", "trigger"):
        assert privilege in normalized
    for table in EXPECTED_TABLES:
        assert table in normalized


def test_backend_only_permissions_protects_schema_sequences_and_defaults() -> None:
    normalized = re.sub(r"\s+", " ", _content().lower())

    assert "revoke usage, create on schema public from public, anon, authenticated" in normalized
    assert "revoke all privileges on all tables in schema public from public, anon, authenticated" in normalized
    assert "revoke all privileges on all sequences in schema public from public, anon, authenticated" in normalized
    assert "alter default privileges in schema public revoke all on tables from public, anon, authenticated" in normalized
    assert "alter default privileges in schema public revoke all on sequences from public, anon, authenticated" in normalized


def test_backend_only_permissions_does_not_mutate_data_or_create_policies() -> None:
    normalized = re.sub(r"\s+", " ", _content().lower())

    forbidden = ("drop table", "drop column", "delete from", "insert into", "update ", "create policy", "alter table")
    for token in forbidden:
        assert token not in normalized
    assert "grant " not in normalized


def test_backend_only_permissions_passes_static_migration_validators() -> None:
    assert migrations.DANGEROUS_SQL_PATTERN.search(_content()) is None
    single.validate_static_sql(MIGRATION_PATH)


def test_rollback_is_manual_explicit_and_not_public() -> None:
    rollback = ROLLBACK_PATH.read_text(encoding="utf-8").lower()
    sql_without_comments = "\n".join(
        line for line in rollback.splitlines() if not line.strip().startswith("--")
    )
    normalized = re.sub(r"\s+", " ", sql_without_comments)

    assert "manual rollback" in rollback
    assert "explicit owner approval" in rollback
    assert re.search(r"\bgrant\b[^;]*\bto public\b", normalized) is None
    assert "to anon, authenticated" in normalized
    assert "drop table" not in normalized
    assert "delete from" not in normalized


def test_backend_only_validation_script_uses_only_temporary_database_env() -> None:
    content = VALIDATION_SCRIPT_PATH.read_text(encoding="utf-8")

    assert "POSTGRES_VALIDATION_URL" in content
    assert "SUPABASE_DIRECT_URL" in content
    assert "postgres_test_only" not in content
    assert "print(validation_url" not in content
    assert "DIRECT_URL" not in content.replace("SUPABASE_DIRECT_URL", "")


def test_backend_only_validation_script_checks_core_behaviour() -> None:
    content = VALIDATION_SCRIPT_PATH.read_text(encoding="utf-8")

    for role in ("anon", "authenticated", "service_role", "backend_app"):
        assert role in content
    assert "permission_validation_temp" in content
    assert "expect_access_denied" in content
    assert "validate_rollback" in content
    assert "assert_counts_preserved" in content
