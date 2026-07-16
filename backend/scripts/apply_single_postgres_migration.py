import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Connection

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.environment import is_postgresql_url, real_data_mode_enabled  # noqa: E402
from app.database.session import normalize_database_url  # noqa: E402
from scripts.apply_postgres_migrations import (  # noqa: E402
    DANGEROUS_SQL_PATTERN,
    INVALID_DIRECT_URL_MESSAGE,
    MIGRATIONS_DIR,
    get_direct_url,
    mask_database_url,
    split_sql_statements,
)

CONFIRMATION_VALUE = "APLICAR-MIGRATION"
NONE_PREVIOUS = "NONE"
ALLOWED_MIGRATIONS = (
    "2026_07_01_000_postgres_bootstrap_schema.sql",
    "2026_07_02_postgres_preparacao.sql",
    "2026_07_12_auth_sessions.sql",
    "2026_07_12_real_data_readiness.sql",
    "2026_07_12_backend_only_permissions.sql",
    "2026_07_15_first_admin_bootstrap.sql",
)
EXPECTED_PREVIOUS = {
    "2026_07_01_000_postgres_bootstrap_schema.sql": NONE_PREVIOUS,
    "2026_07_02_postgres_preparacao.sql": "2026_07_01_000_postgres_bootstrap_schema.sql",
    "2026_07_12_auth_sessions.sql": "2026_07_02_postgres_preparacao.sql",
    "2026_07_12_real_data_readiness.sql": "2026_07_12_auth_sessions.sql",
    "2026_07_12_backend_only_permissions.sql": "2026_07_12_real_data_readiness.sql",
    "2026_07_15_first_admin_bootstrap.sql": "2026_07_12_backend_only_permissions.sql",
}
EXPECTED_TABLES_AFTER_APPLY = {
    "2026_07_01_000_postgres_bootstrap_schema.sql": {
        "leads",
        "clientes",
        "propostas",
        "tarefas",
        "whatsapp_messages",
        "users",
        "audit_logs",
        "consents",
        "simulations",
    },
    "2026_07_02_postgres_preparacao.sql": {
        "leads",
        "clientes",
        "propostas",
        "tarefas",
        "whatsapp_messages",
        "users",
        "audit_logs",
        "consents",
        "simulations",
    },
    "2026_07_12_auth_sessions.sql": {"auth_sessions"},
    "2026_07_12_real_data_readiness.sql": {"backup_audit_logs"},
    "2026_07_12_backend_only_permissions.sql": {
        "leads",
        "clientes",
        "propostas",
        "tarefas",
        "whatsapp_messages",
        "users",
        "audit_logs",
        "consents",
        "simulations",
        "auth_sessions",
        "backup_audit_logs",
        "schema_migrations",
    },
    "2026_07_15_first_admin_bootstrap.sql": {"admin_bootstrap_tokens"},
}
SECRET_PATTERN = re.compile(
    r"(postgres(?:ql)?://[^\s`'\"]+|SUPABASE_SERVICE_ROLE_KEY|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})",
    re.IGNORECASE,
)


def validate_confirmation(confirmation: str) -> None:
    if confirmation != CONFIRMATION_VALUE:
        raise RuntimeError("Confirmacao invalida. Nenhuma migration foi aplicada.")


def validate_selection(migration_name: str, expected_previous: str) -> Path:
    if migration_name not in ALLOWED_MIGRATIONS:
        raise RuntimeError("Migration nao permitida para apply unitario.")
    if expected_previous not in (NONE_PREVIOUS, *ALLOWED_MIGRATIONS[:-1]):
        raise RuntimeError("Migration anterior esperada nao permitida.")
    if EXPECTED_PREVIOUS[migration_name] != expected_previous:
        raise RuntimeError("Ordem invalida para a migration selecionada.")

    migration_path = (MIGRATIONS_DIR / migration_name).resolve()
    migrations_root = MIGRATIONS_DIR.resolve()
    if migrations_root not in migration_path.parents or not migration_path.is_file():
        raise RuntimeError("Arquivo de migration invalido.")
    return migration_path


def file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_static_sql(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    if DANGEROUS_SQL_PATTERN.search(content):
        raise RuntimeError("Operacao destrutiva bloqueada na migration selecionada.")
    if SECRET_PATTERN.search(content):
        raise RuntimeError("Possivel segredo embutido bloqueado na migration selecionada.")

    allowed_prefixes = (
        "CREATE TABLE",
        "CREATE INDEX",
        "CREATE UNIQUE INDEX",
        "ALTER TABLE",
        "ALTER DEFAULT PRIVILEGES",
        "REVOKE",
    )
    for statement in split_sql_statements(content):
        without_comments = "\n".join(
            line for line in statement.splitlines() if not line.strip().startswith("--")
        )
        normalized = re.sub(r"\s+", " ", without_comments.strip()).upper()
        if not normalized.startswith(allowed_prefixes):
            raise RuntimeError("Comando SQL fora do escopo permitido para migrations controladas.")


def ensure_control_table(conn: Connection) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
              version VARCHAR(120) PRIMARY KEY,
              checksum VARCHAR(64) NOT NULL,
              applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def applied_migrations(conn: Connection) -> dict[str, str]:
    try:
        rows = conn.execute(text("SELECT version, checksum FROM schema_migrations")).fetchall()
    except Exception:
        return {}
    return {row[0]: row[1] for row in rows}


def validate_order_and_reapply(
    conn: Connection,
    migration_name: str,
    expected_previous: str,
    *,
    allow_already_applied: bool = False,
) -> bool:
    applied = applied_migrations(conn)
    for applied_name, applied_checksum in applied.items():
        if applied_name in ALLOWED_MIGRATIONS:
            current_checksum = file_checksum(MIGRATIONS_DIR / applied_name)
            if applied_checksum != current_checksum:
                raise RuntimeError("Checksum divergente detectado em migration ja registrada.")

    if migration_name in applied:
        if allow_already_applied:
            return False
        raise RuntimeError("Migration ja aplicada. Reaplicacao bloqueada.")

    if expected_previous == NONE_PREVIOUS:
        if any(name in applied for name in ALLOWED_MIGRATIONS):
            raise RuntimeError("Ordem invalida: ja existem migrations aplicadas.")
        return True

    if expected_previous not in applied:
        raise RuntimeError("Ordem invalida: migration anterior esperada nao esta registrada.")
    return True


def validate_expected_objects(conn: Connection, migration_name: str) -> None:
    existing_tables = set(inspect(conn).get_table_names())
    missing = EXPECTED_TABLES_AFTER_APPLY[migration_name] - existing_tables
    if missing:
        raise RuntimeError("Objetos esperados nao foram encontrados apos o apply.")

    applied = applied_migrations(conn)
    if migration_name not in applied:
        raise RuntimeError("Migration aplicada nao foi registrada na tabela de controle.")


def execute_sql_file(conn: Connection, path: Path) -> None:
    for statement in split_sql_statements(path.read_text(encoding="utf-8")):
        conn.exec_driver_sql(statement)


def run_single_migration(
    *,
    migration_name: str,
    expected_previous: str,
    confirmation: str,
    direct_url: str,
    transaction_test: bool = False,
    allow_already_applied: bool = False,
) -> None:
    validate_confirmation(confirmation)
    migration_path = validate_selection(migration_name, expected_previous)
    validate_static_sql(migration_path)
    checksum = file_checksum(migration_path)

    engine = create_engine(direct_url)
    if transaction_test:
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                ensure_control_table(conn)
                should_apply = validate_order_and_reapply(
                    conn,
                    migration_name,
                    expected_previous,
                    allow_already_applied=allow_already_applied,
                )
                if should_apply:
                    execute_sql_file(conn, migration_path)
            except Exception:
                transaction.rollback()
                raise
            transaction.rollback()
        print(f"TESTE TRANSACIONAL OK: {migration_name}")
        return

    with engine.begin() as conn:
        ensure_control_table(conn)
        should_apply = validate_order_and_reapply(
            conn,
            migration_name,
            expected_previous,
            allow_already_applied=allow_already_applied,
        )
        if not should_apply:
            validate_expected_objects(conn, migration_name)
            print(f"JA APLICADA COM SEGURANCA: {migration_name}")
            return
        execute_sql_file(conn, migration_path)
        conn.execute(
            text("INSERT INTO schema_migrations (version, checksum) VALUES (:version, :checksum)"),
            {"version": migration_name, "checksum": checksum},
        )
        validate_expected_objects(conn, migration_name)
    print(f"APLICADA COM SEGURANCA: {migration_name}")


def get_single_direct_url() -> str:
    direct_url = os.environ.get("DIRECT_URL", "").strip()
    if not direct_url:
        raise RuntimeError("DIRECT_URL ausente. Configure somente como secret seguro antes de rodar migrations.")
    if not is_postgresql_url(direct_url):
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    return normalize_database_url(direct_url)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aplica uma unica migration PostgreSQL sem expor segredos.")
    parser.add_argument("--migration", required=True)
    parser.add_argument("--expected-previous", required=True)
    parser.add_argument("--confirmation", required=True)
    parser.add_argument("--transaction-test", action="store_true")
    parser.add_argument("--allow-already-applied", action="store_true")
    args = parser.parse_args(argv)

    if real_data_mode_enabled():
        raise RuntimeError("Migrations bloqueadas com REAL_DATA_MODE=true nesta fase controlada.")

    direct_url = get_single_direct_url()
    print(f"DIRECT_URL configurada: {mask_database_url(direct_url)}")
    run_single_migration(
        migration_name=args.migration,
        expected_previous=args.expected_previous,
        confirmation=args.confirmation,
        direct_url=direct_url,
        transaction_test=args.transaction_test,
        allow_already_applied=args.allow_already_applied,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
