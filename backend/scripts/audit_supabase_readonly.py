import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.environment import is_postgresql_url  # noqa: E402
from app.database.session import normalize_database_url  # noqa: E402
from app.services.database_target_guard import guard_if_required  # noqa: E402
from scripts.apply_postgres_migrations import INVALID_DIRECT_URL_MESSAGE, mask_database_url  # noqa: E402

REPORT_PATH = REPO_ROOT / "docs" / "audit" / "SUPABASE_READONLY_AUDIT_2026-07-12.md"
EXPECTED_MIGRATIONS = (
    "2026_07_01_000_postgres_bootstrap_schema.sql",
    "2026_07_02_postgres_preparacao.sql",
    "2026_07_12_auth_sessions.sql",
    "2026_07_12_real_data_readiness.sql",
)
EXPECTED_TABLES = {
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
    "schema_migrations",
    "backup_audit_logs",
}
PII_COLUMN_PATTERN = re.compile(r"(cpf|email|telefone|phone|token|senha|password|bank|banco|beneficio)", re.IGNORECASE)
SECRET_VALUE_PATTERN = re.compile(
    r"(postgres(?:ql)?://[^\s`'\"]+|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|SUPABASE_[A-Z_]*KEY|SERVICE_ROLE)",
    re.IGNORECASE,
)
WRITE_SQL_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|UPSERT|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE|COPY|CALL|DO|MERGE|VACUUM|ANALYZE)\b",
    re.IGNORECASE,
)


class SafeReadOnlyConnection:
    def __init__(self, conn: Connection):
        self.conn = conn

    def execute(self, statement: str, params: dict[str, Any] | None = None):
        validate_readonly_sql(statement)
        return self.conn.execute(text(statement), params or {})


def validate_readonly_sql(statement: str) -> None:
    normalized = re.sub(r"\s+", " ", statement.strip())
    if not normalized:
        raise RuntimeError("Consulta vazia bloqueada.")
    if WRITE_SQL_PATTERN.search(normalized):
        raise RuntimeError("Comando de escrita bloqueado em auditoria readonly.")
    if not normalized.upper().startswith("SELECT"):
        raise RuntimeError("Somente SELECT e permitido em auditoria readonly.")


def sanitize_text(value: Any) -> str:
    text_value = str(value)
    text_value = SECRET_VALUE_PATTERN.sub("[OCULTO]", text_value)
    text_value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL_OCULTO]", text_value)
    text_value = re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "[CPF_OCULTO]", text_value)
    text_value = re.sub(r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?9?\d{4}[-\s]?\d{4}\b", "[TELEFONE_OCULTO]", text_value)
    return text_value


def safe_error(exc: Exception) -> str:
    return sanitize_text(exc.__class__.__name__)


def get_direct_url() -> str:
    direct_url = os.environ.get("DIRECT_URL", "").strip()
    if not direct_url:
        raise RuntimeError("DIRECT_URL ausente. Configure somente como secret seguro no GitHub Actions.")
    if not is_postgresql_url(direct_url):
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    normalized = normalize_database_url(direct_url)
    guard_if_required(normalized, os.environ)
    return normalized


def scalar(conn: SafeReadOnlyConnection, statement: str, params: dict[str, Any] | None = None) -> int:
    value = conn.execute(statement, params).scalar()
    return int(value or 0)


def fetch_all(conn: SafeReadOnlyConnection, statement: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [dict(row._mapping) for row in conn.execute(statement, params).fetchall()]


def audit_database(conn: SafeReadOnlyConnection) -> dict[str, Any]:
    migrations = fetch_all(
        conn,
        """
        SELECT version, checksum, applied_at
        FROM schema_migrations
        ORDER BY applied_at, version
        """,
    )
    tables = fetch_all(
        conn,
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
    )
    table_names = [row["table_name"] for row in tables]
    columns = fetch_all(
        conn,
        """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """,
    )
    indexes = fetch_all(
        conn,
        """
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
        """,
    )
    constraints = fetch_all(
        conn,
        """
        SELECT tc.table_name, tc.constraint_name, tc.constraint_type
        FROM information_schema.table_constraints tc
        WHERE tc.table_schema = 'public'
        ORDER BY tc.table_name, tc.constraint_name
        """,
    )
    foreign_keys = fetch_all(
        conn,
        """
        SELECT tc.table_name, tc.constraint_name
        FROM information_schema.table_constraints tc
        WHERE tc.table_schema = 'public' AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, tc.constraint_name
        """,
    )
    triggers = fetch_all(
        conn,
        """
        SELECT event_object_table AS table_name, trigger_name
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        ORDER BY event_object_table, trigger_name
        """,
    )
    functions = fetch_all(
        conn,
        """
        SELECT p.proname AS function_name, p.prosecdef AS security_definer
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'public'
        ORDER BY p.proname
        """,
    )
    policies = fetch_all(
        conn,
        """
        SELECT schemaname, tablename, policyname, permissive, roles, cmd
        FROM pg_policies
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
        """,
    )
    rls = fetch_all(
        conn,
        """
        SELECT relname AS table_name, relrowsecurity AS rls_enabled
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'
        ORDER BY relname
        """,
    )
    grants = fetch_all(
        conn,
        """
        SELECT grantee, table_name, privilege_type
        FROM information_schema.role_table_grants
        WHERE table_schema = 'public'
        ORDER BY table_name, grantee, privilege_type
        """,
    )

    row_counts = {}
    for table_name in table_names:
        if table_name == "schema_migrations":
            row_counts[table_name] = len(migrations)
        else:
            row_counts[table_name] = scalar(conn, f'SELECT COUNT(*) FROM public."{table_name}"')

    column_names_by_table: dict[str, set[str]] = {}
    for column in columns:
        column_names_by_table.setdefault(column["table_name"], set()).add(column["column_name"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "migrations": migrations,
        "tables": table_names,
        "columns": columns,
        "indexes": indexes,
        "constraints": constraints,
        "foreign_keys": foreign_keys,
        "triggers": triggers,
        "functions": functions,
        "policies": policies,
        "rls": rls,
        "grants": grants,
        "row_counts": row_counts,
        "column_names_by_table": {key: sorted(value) for key, value in column_names_by_table.items()},
    }


def classify(report: dict[str, Any]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    migration_names = [row["version"] for row in report["migrations"]]
    if migration_names != list(EXPECTED_MIGRATIONS):
        blockers.append("schema_migrations nao contem exatamente as quatro migrations esperadas na ordem esperada.")
    missing_tables = sorted(EXPECTED_TABLES - set(report["tables"]))
    unexpected_tables = sorted(set(report["tables"]) - EXPECTED_TABLES)
    if missing_tables:
        blockers.append(f"Tabelas esperadas ausentes: {', '.join(missing_tables)}.")
    if unexpected_tables:
        blockers.append(f"Tabelas inesperadas encontradas: {', '.join(unexpected_tables)}.")
    if any(count for table, count in report["row_counts"].items() if table != "schema_migrations"):
        blockers.append("Existem registros fora de schema_migrations; verificar se todos sao ficticios antes da proxima etapa.")

    auth_columns = set(report["column_names_by_table"].get("auth_sessions", []))
    if "session_id_hash" not in auth_columns or any(column == "token" for column in auth_columns):
        blockers.append("auth_sessions nao atende ao padrao esperado de hash sem token completo.")

    if blockers:
        return "C) BLOQUEADO", blockers
    return "A) BANCO APROVADO PARA PROXIMA ETAPA", ["Nenhum bloqueador encontrado."]


def count_unexpected_pii_columns(columns: list[dict[str, Any]]) -> int:
    return sum(1 for column in columns if PII_COLUMN_PATTERN.search(column["column_name"]))


def render_report(report: dict[str, Any]) -> str:
    decision, blockers = classify(report)
    expected_missing = sorted(EXPECTED_TABLES - set(report["tables"]))
    unexpected_tables = sorted(set(report["tables"]) - EXPECTED_TABLES)
    auth_columns = report["column_names_by_table"].get("auth_sessions", [])
    personal_tables = ["leads", "clientes", "propostas", "tarefas", "whatsapp_messages", "consents", "simulations"]
    soft_delete_ok = all("deleted_at" in report["column_names_by_table"].get(table, []) for table in personal_tables)
    timestamps_ok = all(
        {"created_at", "updated_at"}.issubset(set(report["column_names_by_table"].get(table, [])))
        for table in EXPECTED_TABLES
        if table != "schema_migrations"
    )
    lines = [
        "# AUDITORIA READONLY SUPABASE",
        "",
        f"Gerado em UTC: {sanitize_text(report['generated_at'])}",
        "",
        "## Migrations",
        f"- Total registrado: {len(report['migrations'])}",
        f"- Ordem: {'OK' if [row['version'] for row in report['migrations']] == list(EXPECTED_MIGRATIONS) else 'DIVERGENTE'}",
        f"- Checksums registrados: {'sim' if all(row.get('checksum') for row in report['migrations']) else 'nao'}",
        "",
        "## Estrutura",
        f"- Tabelas: {len(report['tables'])}",
        f"- Indices: {len(report['indexes'])}",
        f"- Constraints: {len(report['constraints'])}",
        f"- Triggers: {len(report['triggers'])}",
        f"- Functions: {len(report['functions'])}",
        "",
        "## Tabelas",
        f"- Esperadas ausentes: {', '.join(expected_missing) if expected_missing else 'nenhuma'}",
        f"- Inesperadas: {', '.join(unexpected_tables) if unexpected_tables else 'nenhuma'}",
        "",
        "## Indices",
        f"- Total: {len(report['indexes'])}",
        "",
        "## Constraints",
        f"- Total: {len(report['constraints'])}",
        f"- Foreign keys: {len(report['foreign_keys'])}",
        "",
        "## Auth sessions",
        f"- Existe: {'auth_sessions' in report['tables']}",
        f"- Campos esperados: {', '.join(auth_columns)}",
        f"- Token completo armazenado: {'sim' if 'token' in auth_columns else 'nao'}",
        f"- Registros: {report['row_counts'].get('auth_sessions', 0)}",
        "",
        "## Auditoria",
        f"- audit_logs existe: {'audit_logs' in report['tables']}",
        f"- Registros: {report['row_counts'].get('audit_logs', 0)}",
        "",
        "## Consentimentos",
        f"- consents existe: {'consents' in report['tables']}",
        f"- Registros: {report['row_counts'].get('consents', 0)}",
        "",
        "## Simulacoes",
        f"- simulations existe: {'simulations' in report['tables']}",
        f"- Registros: {report['row_counts'].get('simulations', 0)}",
        "",
        "## Soft delete",
        f"- Campos presentes nas tabelas esperadas: {'sim' if soft_delete_ok else 'nao'}",
        "",
        "## RLS e permissoes",
        f"- Politicas RLS: {len(report['policies'])}",
        f"- Tabelas com RLS ativo: {sum(1 for row in report['rls'] if row['rls_enabled'])}",
        f"- Grants auditados: {len(report['grants'])}",
        f"- Functions SECURITY DEFINER: {sum(1 for row in report['functions'] if row['security_definer'])}",
        "",
        "## Dados existentes",
        f"- Registros por tabela: {json.dumps(report['row_counts'], sort_keys=True)}",
        f"- Dados pessoais exibidos: nao",
        f"- Colunas sensiveis esperadas auditadas: {count_unexpected_pii_columns(report['columns'])}",
        "",
        "## Divergencias",
        f"- Timestamps: {'OK' if timestamps_ok else 'DIVERGENTE'}",
        f"- DATA-MODEL: {'OK' if not expected_missing else 'DIVERGENTE'}",
        f"- Models backend: {'OK' if not expected_missing else 'DIVERGENTE'}",
        f"- Migrations: {'OK' if [row['version'] for row in report['migrations']] == list(EXPECTED_MIGRATIONS) else 'DIVERGENTE'}",
        "",
        "## Bloqueadores",
        *[f"- {sanitize_text(blocker)}" for blocker in blockers],
        "",
        "## Decisao",
        decision,
        "",
    ]
    return sanitize_text("\n".join(lines))


def run_audit(direct_url: str, output_path: Path = REPORT_PATH) -> str:
    print(f"DIRECT_URL configurada: {mask_database_url(direct_url)}")
    engine = create_engine(direct_url)
    with engine.connect() as raw_conn:
        raw_conn.execute(text("BEGIN READ ONLY"))
        try:
            conn = SafeReadOnlyConnection(raw_conn)
            report = audit_database(conn)
            rendered = render_report(report)
        except Exception as exc:
            raw_conn.execute(text("ROLLBACK"))
            raise RuntimeError(f"Auditoria readonly falhou com erro seguro: {safe_error(exc)}") from exc
        raw_conn.execute(text("ROLLBACK"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audita Supabase em modo somente leitura sem expor segredos.")
    parser.add_argument("--output", default=str(REPORT_PATH))
    args = parser.parse_args(argv)

    direct_url = get_direct_url()
    report = run_audit(direct_url, Path(args.output))
    print(report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {sanitize_text(exc)}", file=sys.stderr)
        raise SystemExit(1)
