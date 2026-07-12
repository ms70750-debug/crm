import os
import sys
from pathlib import Path
from typing import Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.apply_postgres_migrations import split_sql_statements  # noqa: E402

MIGRATIONS_DIR = BACKEND_ROOT / "migrations" / "postgres"
ROLLBACK_DIR = MIGRATIONS_DIR / "rollback"
ORDERED_MIGRATIONS = (
    "2026_07_01_000_postgres_bootstrap_schema.sql",
    "2026_07_02_postgres_preparacao.sql",
    "2026_07_12_auth_sessions.sql",
    "2026_07_12_real_data_readiness.sql",
    "2026_07_12_backend_only_permissions.sql",
)
PRE_SECURITY_MIGRATIONS = ORDERED_MIGRATIONS[:-1]
BACKEND_ONLY_MIGRATION = ORDERED_MIGRATIONS[-1]
ROLLBACK_MIGRATION = "2026_07_12_backend_only_permissions_down.sql"
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
DIRECT_ROLES = ("anon", "authenticated")
VALIDATED_PRIVILEGES = ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER")
TEMP_TABLE = "permission_validation_temp"


def validation_url() -> str:
    if os.environ.get("SUPABASE_DIRECT_URL"):
        raise RuntimeError("SUPABASE_DIRECT_URL nao deve ser usado nesta validacao.")
    url = os.environ.get("POSTGRES_VALIDATION_URL", "").strip()
    if not url:
        raise RuntimeError("POSTGRES_VALIDATION_URL ausente para PostgreSQL temporario.")
    return url


def execute_sql_file(conn: Connection, path: Path) -> None:
    for statement in split_sql_statements(path.read_text(encoding="utf-8")):
        conn.exec_driver_sql(statement)


def apply_migration(conn: Connection, name: str) -> None:
    path = MIGRATIONS_DIR / name
    execute_sql_file(conn, path)
    checksum = "validation-only"
    conn.execute(
        text(
            """
            INSERT INTO schema_migrations (version, checksum)
            VALUES (:version, :checksum)
            ON CONFLICT (version) DO NOTHING
            """
        ),
        {"version": name, "checksum": checksum},
    )


def ensure_control_and_roles(conn: Connection) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version VARCHAR(120) PRIMARY KEY,
              checksum VARCHAR(64) NOT NULL DEFAULT 'validation-only',
              applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    for role in ("anon", "authenticated", "service_role", "backend_app"):
        conn.exec_driver_sql(
            f"""
            DO $$
            BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') THEN
                CREATE ROLE {role} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
              END IF;
            END
            $$;
            """
        )


def seed_initial_supabase_like_grants(conn: Connection) -> None:
    conn.execute(text("GRANT USAGE, CREATE ON SCHEMA public TO postgres"))
    conn.execute(text("GRANT USAGE ON SCHEMA public TO anon, authenticated, backend_app"))
    conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public TO anon, authenticated"))
    conn.execute(text("GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated"))
    conn.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public TO backend_app"))
    conn.execute(text("GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO backend_app"))


def table_privileges(conn: Connection, role: str, table_name: str) -> set[str]:
    rows = conn.execute(
        text(
            """
            SELECT privilege_type
            FROM information_schema.role_table_grants
            WHERE table_schema = 'public'
              AND grantee = :role
              AND table_name = :table_name
            """
        ),
        {"role": role, "table_name": table_name},
    ).scalars()
    return {str(row) for row in rows}


def schema_privileges(conn: Connection, role: str) -> set[str]:
    privileges = set()
    for privilege in ("USAGE", "CREATE"):
        allowed = conn.execute(
            text("SELECT has_schema_privilege(:role, 'public', :privilege)"),
            {"role": role, "privilege": privilege},
        ).scalar()
        if allowed:
            privileges.add(privilege)
    return privileges


def public_schema_has_access(conn: Connection) -> bool:
    acl = conn.execute(
        text(
            """
            SELECT COALESCE(nspacl::text, '')
            FROM pg_namespace
            WHERE nspname = 'public'
            """
        )
    ).scalar_one()
    entries = acl.strip("{}").split(",") if acl else []
    return any(entry.startswith("=") for entry in entries)


def sequence_grants(conn: Connection, role: str) -> int:
    return int(
        conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.role_usage_grants
                WHERE object_schema = 'public'
                  AND grantee = :role
                  AND object_type = 'SEQUENCE'
                """
            ),
            {"role": role},
        ).scalar()
        or 0
    )


def assert_no_direct_role_grants(conn: Connection) -> None:
    for role in DIRECT_ROLES:
        for table_name in EXPECTED_TABLES:
            grants = table_privileges(conn, role, table_name)
            leaked = grants & set(VALIDATED_PRIVILEGES)
            if leaked:
                raise RuntimeError(f"{role} possui grants indevidos em {table_name}: {sorted(leaked)}")
        schema = schema_privileges(conn, role)
        if schema:
            raise RuntimeError(f"{role} possui privilegios indevidos no schema public: {sorted(schema)}")
        if sequence_grants(conn, role):
            raise RuntimeError(f"{role} possui grants indevidos em sequences.")


def assert_public_has_no_access(conn: Connection) -> None:
    for table_name in EXPECTED_TABLES:
        grants = table_privileges(conn, "PUBLIC", table_name) | table_privileges(conn, "public", table_name)
        if grants:
            raise RuntimeError(f"PUBLIC possui grants indevidos em {table_name}: {sorted(grants)}")
    if public_schema_has_access(conn):
        raise RuntimeError("PUBLIC possui privilegios indevidos no schema public.")


def assert_role_is_not_superuser(conn: Connection, roles: Iterable[str]) -> None:
    rows = conn.execute(
        text("SELECT rolname, rolsuper FROM pg_roles WHERE rolname = ANY(:roles)"),
        {"roles": list(roles)},
    ).fetchall()
    offenders = [row.rolname for row in rows if row.rolsuper]
    if offenders:
        raise RuntimeError(f"Roles com superuser indevido: {offenders}")


def expect_access_denied(conn: Connection, role: str, statement: str) -> None:
    nested = conn.begin_nested()
    try:
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        conn.execute(text(statement))
    except Exception:
        nested.rollback()
        conn.execute(text("RESET ROLE"))
        return
    nested.rollback()
    conn.execute(text("RESET ROLE"))
    raise RuntimeError(f"{role} executou acesso direto indevido: {statement}")


def execute_as_role(conn: Connection, role: str, statement: str, params: dict | None = None) -> None:
    nested = conn.begin_nested()
    try:
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        conn.execute(text(statement), params or {})
    except Exception:
        nested.rollback()
        conn.execute(text("RESET ROLE"))
        raise
    nested.commit()
    conn.execute(text("RESET ROLE"))


def seed_fictitious_data(conn: Connection) -> None:
    conn.execute(
        text(
            """
            INSERT INTO clientes (nome, cpf, telefone, email, convenio, created_at, updated_at)
            VALUES ('Cliente Validacao Ficticio', '000.000.000-00', '11900000000', 'validacao@example.test', 'INSS', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        )
    )
    customer_id = conn.execute(text("SELECT id FROM clientes WHERE email = 'validacao@example.test'")).scalar_one()
    conn.execute(
        text(
            """
            INSERT INTO consents (customer_id, channel, granted, purpose, status, source, created_at, updated_at)
            VALUES (:customer_id, 'whatsapp', TRUE, 'validacao', 'active', 'postgres-temporario', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        ),
        {"customer_id": customer_id},
    )
    conn.execute(
        text(
            """
            INSERT INTO audit_logs (actor, action, entity_type, entity_id, metadata_json, created_at, updated_at)
            VALUES ('validation', 'backend_only_check', 'clientes', :customer_id, '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
        ),
        {"customer_id": customer_id},
    )


def counts(conn: Connection) -> dict[str, int]:
    return {
        table_name: int(conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar() or 0)
        for table_name in EXPECTED_TABLES
    }


def assert_counts_not_decreased(before: dict[str, int], after: dict[str, int]) -> None:
    for table_name, count in before.items():
        if after[table_name] < count:
            raise RuntimeError(f"Linhas removidas em {table_name}: {count} -> {after[table_name]}")


def validate_no_tables_or_columns_removed(conn: Connection, baseline_columns: dict[str, set[str]]) -> None:
    rows = conn.execute(
        text(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            """
        )
    ).fetchall()
    current: dict[str, set[str]] = {}
    for row in rows:
        current.setdefault(row.table_name, set()).add(row.column_name)
    missing_tables = set(baseline_columns) - set(current)
    if missing_tables:
        raise RuntimeError(f"Tabelas removidas: {sorted(missing_tables)}")
    for table_name, columns in baseline_columns.items():
        missing_columns = columns - current[table_name]
        if missing_columns:
            raise RuntimeError(f"Colunas removidas em {table_name}: {sorted(missing_columns)}")


def column_snapshot(conn: Connection) -> dict[str, set[str]]:
    rows = conn.execute(
        text(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = ANY(:tables)
            """
        ),
        {"tables": list(EXPECTED_TABLES)},
    ).fetchall()
    snapshot: dict[str, set[str]] = {}
    for row in rows:
        snapshot.setdefault(row.table_name, set()).add(row.column_name)
    return snapshot


def validate_pre_security_state(conn: Connection) -> None:
    if "CREATE" not in schema_privileges(conn, "postgres"):
        raise RuntimeError("postgres nao manteve CREATE administrativo no schema public.")
    for role in DIRECT_ROLES:
        grants = table_privileges(conn, role, "clientes")
        if not {"SELECT", "INSERT", "UPDATE", "DELETE"}.issubset(grants):
            raise RuntimeError(f"{role} nao possui grants simulados esperados antes da migration.")
    if table_privileges(conn, "PUBLIC", "clientes") or table_privileges(conn, "public", "clientes"):
        raise RuntimeError("PUBLIC recebeu acesso inesperado antes da migration backend-only.")
    assert_role_is_not_superuser(conn, ("anon", "authenticated", "service_role", "backend_app"))


def validate_backend_crud(conn: Connection) -> None:
    execute_as_role(
        conn,
        "backend_app",
        """
        INSERT INTO clientes (nome, cpf, telefone, email, convenio, created_at, updated_at)
        VALUES ('Cliente Backend App', '000.000.000-01', '11900000001', 'backend@example.test', 'INSS', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
    )
    execute_as_role(
        conn,
        "backend_app",
        "UPDATE clientes SET observacoes = 'crud ficticio ok' WHERE email = 'backend@example.test'",
    )
    execute_as_role(conn, "backend_app", "SELECT id FROM clientes WHERE email = 'backend@example.test'")
    execute_as_role(conn, "backend_app", "DELETE FROM clientes WHERE email = 'backend@example.test'")


def validate_default_privileges(conn: Connection) -> None:
    conn.execute(text(f"CREATE TABLE {TEMP_TABLE} (id SERIAL PRIMARY KEY)"))
    try:
        for role in ("anon", "authenticated", "PUBLIC", "public"):
            grants = table_privileges(conn, role, TEMP_TABLE)
            if grants:
                raise RuntimeError(f"{role} recebeu grants na tabela temporaria: {sorted(grants)}")
    finally:
        conn.execute(text(f"DROP TABLE IF EXISTS {TEMP_TABLE}"))


def validate_rollback(conn: Connection, before: dict[str, int]) -> None:
    execute_sql_file(conn, ROLLBACK_DIR / ROLLBACK_MIGRATION)
    for role in DIRECT_ROLES:
        for table_name in EXPECTED_TABLES:
            grants = table_privileges(conn, role, table_name)
            if set(VALIDATED_PRIVILEGES) - grants:
                raise RuntimeError(f"Rollback nao restaurou grants documentados para {role} em {table_name}.")
    assert_public_has_no_access(conn)
    assert_counts_not_decreased(before, counts(conn))


def run_validation() -> None:
    engine = create_engine(validation_url())
    with engine.begin() as conn:
        ensure_control_and_roles(conn)
        for migration_name in PRE_SECURITY_MIGRATIONS:
            apply_migration(conn, migration_name)
        seed_initial_supabase_like_grants(conn)
        validate_pre_security_state(conn)
        seed_fictitious_data(conn)
        before_counts = counts(conn)
        before_columns = column_snapshot(conn)

        apply_migration(conn, BACKEND_ONLY_MIGRATION)

        assert_no_direct_role_grants(conn)
        assert_public_has_no_access(conn)
        assert_role_is_not_superuser(conn, ("anon", "authenticated", "service_role", "backend_app"))
        validate_backend_crud(conn)
        expect_access_denied(conn, "anon", "SELECT id FROM clientes LIMIT 1")
        expect_access_denied(conn, "anon", "INSERT INTO clientes (nome, cpf, telefone, convenio) VALUES ('Anon', '000', '000', 'INSS')")
        expect_access_denied(conn, "authenticated", "SELECT id FROM clientes LIMIT 1")
        expect_access_denied(conn, "authenticated", "UPDATE clientes SET nome = 'Falha' WHERE id = -1")
        assert_counts_not_decreased(before_counts, counts(conn))
        validate_no_tables_or_columns_removed(conn, before_columns)
        validate_default_privileges(conn)
        validate_rollback(conn, before_counts)

    print("PostgreSQL backend-only validation OK")
    print("Migrations: 5")
    print("Roles bloqueadas: PUBLIC, anon, authenticated")
    print("Backend role funcional: backend_app")
    print("Rollback: OK")


def main() -> int:
    run_validation()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
