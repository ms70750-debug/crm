from pathlib import Path

import pytest

from scripts import audit_supabase_readonly as audit


def test_readonly_validator_allows_select() -> None:
    audit.validate_readonly_sql("SELECT table_name FROM information_schema.tables")


@pytest.mark.parametrize("statement", ["INSERT INTO x VALUES (1)", "UPDATE x SET a = 1", "DELETE FROM x", "CREATE TABLE x (id int)", "ALTER TABLE x ADD COLUMN y int", "DROP TABLE x"])
def test_readonly_validator_blocks_write_commands(statement: str) -> None:
    with pytest.raises(RuntimeError, match="bloqueado|Somente SELECT"):
        audit.validate_readonly_sql(statement)


def test_safe_error_masks_exception_details() -> None:
    exc = RuntimeError("postgresql://user:secret@db.example.com:5432/postgres")

    assert audit.safe_error(exc) == "RuntimeError"


def test_sanitize_text_masks_secrets_and_personal_data() -> None:
    raw = "postgresql://user:secret@db.example.com:5432/postgres admin@demo.com 123.456.789-09 11999998888"
    sanitized = audit.sanitize_text(raw)

    assert "secret" not in sanitized
    assert "db.example.com" not in sanitized
    assert "admin@demo.com" not in sanitized
    assert "123.456.789-09" not in sanitized
    assert "11999998888" not in sanitized


def test_report_contains_only_metadata_and_counts(tmp_path: Path) -> None:
    report = {
        "generated_at": "2026-07-12T00:00:00+00:00",
        "migrations": [
            {"version": name, "checksum": "a" * 64, "applied_at": "2026-07-12T00:00:00+00:00"}
            for name in audit.EXPECTED_MIGRATIONS
        ],
        "tables": sorted(audit.EXPECTED_TABLES),
        "columns": [
            {"table_name": "auth_sessions", "column_name": "session_id_hash", "data_type": "character varying", "is_nullable": "NO"},
            {"table_name": "auth_sessions", "column_name": "user_id", "data_type": "integer", "is_nullable": "NO"},
            {"table_name": "auth_sessions", "column_name": "created_at", "data_type": "timestamp with time zone", "is_nullable": "YES"},
            {"table_name": "auth_sessions", "column_name": "expires_at", "data_type": "timestamp with time zone", "is_nullable": "NO"},
            {"table_name": "auth_sessions", "column_name": "revoked_at", "data_type": "timestamp with time zone", "is_nullable": "YES"},
        ],
        "indexes": [{"tablename": "auth_sessions", "indexname": "ix_auth_sessions_session_id_hash"}],
        "constraints": [{"table_name": "auth_sessions", "constraint_name": "auth_sessions_pkey", "constraint_type": "PRIMARY KEY"}],
        "foreign_keys": [],
        "triggers": [],
        "functions": [],
        "policies": [],
        "rls": [{"table_name": table, "rls_enabled": False} for table in audit.EXPECTED_TABLES],
        "grants": [],
        "row_counts": {table: 0 for table in audit.EXPECTED_TABLES},
        "column_names_by_table": {table: ["created_at", "updated_at", "deleted_at"] for table in audit.EXPECTED_TABLES},
    }
    report["row_counts"]["schema_migrations"] = 4
    report["column_names_by_table"]["auth_sessions"] = ["id", "session_id_hash", "user_id", "created_at", "expires_at", "revoked_at", "updated_at"]

    rendered = audit.render_report(report)

    assert "# AUDITORIA READONLY SUPABASE" in rendered
    assert "Total registrado: 4" in rendered
    assert "Dados pessoais exibidos: nao" in rendered
    assert "A) BANCO APROVADO PARA PROXIMA ETAPA" in rendered
    assert "session_id_hash" in rendered
    assert "token completo armazenado: sim" not in rendered.lower()


def test_report_blocks_unexpected_data_rows() -> None:
    report = {
        "generated_at": "2026-07-12T00:00:00+00:00",
        "migrations": [{"version": name, "checksum": "a" * 64, "applied_at": "x"} for name in audit.EXPECTED_MIGRATIONS],
        "tables": sorted(audit.EXPECTED_TABLES),
        "columns": [],
        "indexes": [],
        "constraints": [],
        "foreign_keys": [],
        "triggers": [],
        "functions": [],
        "policies": [],
        "rls": [],
        "grants": [],
        "row_counts": {table: 0 for table in audit.EXPECTED_TABLES},
        "column_names_by_table": {"auth_sessions": ["session_id_hash", "user_id", "created_at", "expires_at", "revoked_at"]},
    }
    report["row_counts"]["clientes"] = 1

    decision, blockers = audit.classify(report)

    assert decision == "C) BLOQUEADO"
    assert any("registros fora de schema_migrations" in blocker for blocker in blockers)
