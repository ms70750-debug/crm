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
from scripts.apply_postgres_migrations import INVALID_DIRECT_URL_MESSAGE, mask_database_url  # noqa: E402
from scripts.audit_supabase_readonly import sanitize_text, validate_readonly_sql  # noqa: E402

REPORT_PATH = REPO_ROOT / "docs" / "audit" / "SUPABASE_PERMISSIONS_AUDIT_2026-07-12.md"
EXPECTED_TABLES = (
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
)
SENSITIVE_TABLES = {
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
}
PUBLIC_ROLES = {"PUBLIC", "public"}
DIRECT_ROLES = {"anon", "authenticated"}
BACKEND_ROLES = {"service_role", "postgres"}
WRITE_PRIVILEGES = {"INSERT", "UPDATE", "DELETE", "TRUNCATE"}
READ_PRIVILEGES = {"SELECT"}


class SafeReadOnlyConnection:
    def __init__(self, conn: Connection):
        self.conn = conn

    def execute(self, statement: str, params: dict[str, Any] | None = None):
        validate_readonly_sql(statement)
        return self.conn.execute(text(statement), params or {})


def fetch_all(conn: SafeReadOnlyConnection, statement: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [dict(row._mapping) for row in conn.execute(statement, params).fetchall()]


def safe_error(exc: Exception) -> str:
    return sanitize_text(exc.__class__.__name__)


def get_direct_url() -> str:
    direct_url = os.environ.get("DIRECT_URL", "").strip()
    if not direct_url:
        raise RuntimeError("DIRECT_URL ausente. Configure somente como secret seguro no GitHub Actions.")
    if not is_postgresql_url(direct_url):
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    return normalize_database_url(direct_url)


def grants_by_role(grants: list[dict[str, Any]], table_name: str, role: str) -> set[str]:
    return {
        grant["privilege_type"]
        for grant in grants
        if grant["table_name"] == table_name and grant["grantee"] == role
    }


def policies_for_table(policies: list[dict[str, Any]], table_name: str) -> list[dict[str, Any]]:
    return [policy for policy in policies if policy["tablename"] == table_name]


def classify_table(table: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    public_grants = set(table["grants"].get("public", [])) | set(table["grants"].get("PUBLIC", []))
    anon_grants = set(table["grants"].get("anon", []))
    authenticated_grants = set(table["grants"].get("authenticated", []))

    if public_grants:
        reasons.append("public possui permissao direta")
    if anon_grants & (READ_PRIVILEGES | WRITE_PRIVILEGES):
        reasons.append("anon possui leitura ou escrita direta")
    if authenticated_grants:
        reasons.append("authenticated possui acesso direto sem justificativa backend-only")
    if table["name"] in SENSITIVE_TABLES and (anon_grants or authenticated_grants or public_grants):
        reasons.append("tabela sensivel acessivel fora do backend")
    if table["security_definer_functions"]:
        reasons.append("function SECURITY DEFINER no schema public requer revisao")

    if reasons:
        return "CRITICO", reasons
    if not table["rls_enabled"]:
        return "ATENCAO", ["RLS desativado; aceitavel somente se estrategia backend-only revogar acesso direto"]
    return "SEGURO", ["Sem grants diretos perigosos identificados"]


def recommend_strategy(classified_tables: list[dict[str, Any]], frontend_uses_supabase: bool = False) -> str:
    if frontend_uses_supabase:
        return "B) RLS OBRIGATORIO"
    return "A) BACKEND-ONLY"


def audit_permissions(conn: SafeReadOnlyConnection) -> dict[str, Any]:
    table_rows = fetch_all(
        conn,
        """
        SELECT c.relname AS table_name,
               pg_get_userbyid(c.relowner) AS owner,
               c.relrowsecurity AS rls_enabled,
               c.relforcerowsecurity AS rls_forced
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r'
        ORDER BY c.relname
        """,
    )
    grants = fetch_all(
        conn,
        """
        SELECT grantee, table_name, privilege_type
        FROM information_schema.role_table_grants
        WHERE table_schema = 'public'
        UNION ALL
        SELECT grantee, table_name, privilege_type
        FROM information_schema.table_privileges
        WHERE table_schema = 'public'
        ORDER BY table_name, grantee, privilege_type
        """,
    )
    routine_privileges = fetch_all(
        conn,
        """
        SELECT grantee, routine_name, privilege_type
        FROM information_schema.routine_privileges
        WHERE routine_schema = 'public'
        ORDER BY routine_name, grantee, privilege_type
        """,
    )
    roles = fetch_all(
        conn,
        """
        SELECT rolname
        FROM pg_roles
        WHERE rolname IN ('anon', 'authenticated', 'service_role', 'postgres')
        ORDER BY rolname
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
    security_definer_functions = fetch_all(
        conn,
        """
        SELECT p.proname AS function_name
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'public' AND p.prosecdef = true
        ORDER BY p.proname
        """,
    )

    security_definer_names = {row["function_name"] for row in security_definer_functions}
    classified_tables = []
    for row in table_rows:
        table_name = row["table_name"]
        table_grants: dict[str, list[str]] = {}
        for role in ("public", "PUBLIC", "anon", "authenticated", "service_role", "postgres"):
            table_grants[role] = sorted(grants_by_role(grants, table_name, role))
        table_report = {
            "name": table_name,
            "owner": row["owner"],
            "rls_enabled": bool(row["rls_enabled"]),
            "rls_forced": bool(row["rls_forced"]),
            "policies": policies_for_table(policies, table_name),
            "grants": table_grants,
            "security_definer_functions": sorted(security_definer_names),
        }
        status, reasons = classify_table(table_report)
        table_report["classification"] = status
        table_report["reasons"] = reasons
        classified_tables.append(table_report)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roles": roles,
        "grants": grants,
        "routine_privileges": routine_privileges,
        "policies": policies,
        "tables": classified_tables,
        "security_definer_functions": security_definer_functions,
    }


def count_grants_for(report: dict[str, Any], role: str) -> int:
    return sum(1 for grant in report["grants"] if grant["grantee"] == role)


def render_report(report: dict[str, Any]) -> str:
    tables = report["tables"]
    critical = [table for table in tables if table["classification"] == "CRITICO"]
    attention = [table for table in tables if table["classification"] == "ATENCAO"]
    safe = [table for table in tables if table["classification"] == "SEGURO"]
    missing = sorted(set(EXPECTED_TABLES) - {table["name"] for table in tables})
    unexpected = sorted({table["name"] for table in tables} - set(EXPECTED_TABLES))
    recommendation = recommend_strategy(tables)

    lines = [
        "# AUDITORIA DE PERMISSOES SUPABASE",
        "",
        f"Gerado em UTC: {report['generated_at']}",
        "",
        "## Resumo",
        f"- Grants public: {count_grants_for(report, 'public') + count_grants_for(report, 'PUBLIC')}",
        f"- Grants anon: {count_grants_for(report, 'anon')}",
        f"- Grants authenticated: {count_grants_for(report, 'authenticated')}",
        f"- Grants service_role: {count_grants_for(report, 'service_role')}",
        f"- Grants postgres: {count_grants_for(report, 'postgres')}",
        f"- Tabelas criticas: {len(critical)}",
        f"- Tabelas em atencao: {len(attention)}",
        f"- Tabelas seguras: {len(safe)}",
        f"- Tabelas esperadas ausentes: {', '.join(missing) if missing else 'nenhuma'}",
        f"- Tabelas inesperadas: {', '.join(unexpected) if unexpected else 'nenhuma'}",
        "",
        "## Tabelas",
    ]
    for table in tables:
        lines.extend(
            [
                f"### {table['name']}",
                f"- Classificacao: {table['classification']}",
                f"- Owner: {table['owner']}",
                f"- RLS ativo: {table['rls_enabled']}",
                f"- RLS forcado: {table['rls_forced']}",
                f"- Policies: {len(table['policies'])}",
                f"- Grants public: {table['grants'].get('public', []) or table['grants'].get('PUBLIC', [])}",
                f"- Grants anon: {table['grants'].get('anon', [])}",
                f"- Grants authenticated: {table['grants'].get('authenticated', [])}",
                f"- Grants service_role: {table['grants'].get('service_role', [])}",
                f"- Grants postgres: {table['grants'].get('postgres', [])}",
                f"- Motivos: {'; '.join(table['reasons'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## Funcoes",
            f"- SECURITY DEFINER: {len(report['security_definer_functions'])}",
            f"- Routine privileges auditados: {len(report['routine_privileges'])}",
            "",
            "## Recomendacao",
            recommendation,
            "",
            "## Observacao",
            "- Para USO PROPRIO e backend como unico caminho autorizado, a estrategia preferencial e BACKEND-ONLY: revogar acessos diretos de public, anon e authenticated em etapa futura aprovada. RLS pode ser defesa adicional, mas nao substitui o bloqueio de acesso direto quando o frontend nao usa Supabase.",
            "",
        ]
    )
    return sanitize_text("\n".join(lines))


def run_audit(direct_url: str, output_path: Path) -> str:
    print(f"DIRECT_URL configurada: {mask_database_url(direct_url)}")
    engine = create_engine(direct_url)
    with engine.connect() as raw_conn:
        raw_conn.execute(text("BEGIN READ ONLY"))
        try:
            report = audit_permissions(SafeReadOnlyConnection(raw_conn))
            rendered = render_report(report)
        except Exception as exc:
            raw_conn.execute(text("ROLLBACK"))
            raise RuntimeError(f"Auditoria de permissoes falhou com erro seguro: {safe_error(exc)}") from exc
        raw_conn.execute(text("ROLLBACK"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audita grants e RLS do Supabase sem alterar banco.")
    parser.add_argument("--output", default=str(REPO_ROOT / "docs" / "audit" / "SUPABASE_PERMISSIONS_AUDIT_2026-07-12.md"))
    args = parser.parse_args(argv)
    rendered = run_audit(get_direct_url(), Path(args.output))
    print(rendered)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {sanitize_text(exc)}", file=sys.stderr)
        raise SystemExit(1)
