import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy import create_engine, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.environment import is_postgresql_url, real_data_mode_enabled  # noqa: E402
from app.database.session import normalize_database_url  # noqa: E402

MIGRATIONS_DIR = BACKEND_ROOT / "migrations" / "postgres"
PLACEHOLDER_DIRECT_URL_MESSAGE = "DIRECT_URL ainda contem [YOUR-PASSWORD]. Substitua pela senha real no Secret do GitHub."
INVALID_DIRECT_URL_MESSAGE = (
    "DIRECT_URL invalida. Confira o Secret SUPABASE_DIRECT_URL no GitHub. "
    "Use uma senha sem caracteres reservados ou URL-encode a senha."
)


def parse_direct_url_safely(database_url: str):
    if "[YOUR-PASSWORD]" in database_url:
        raise RuntimeError(PLACEHOLDER_DIRECT_URL_MESSAGE)
    if "[" in database_url or "]" in database_url:
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    try:
        parsed = urlsplit(database_url)
        _ = parsed.port
    except ValueError as exc:
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE) from exc
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    return parsed


def mask_database_url(database_url: str) -> str:
    try:
        parsed = parse_direct_url_safely(database_url)
    except RuntimeError:
        return "<DIRECT_URL invalida ocultada>"
    if not parsed.scheme:
        return "<valor oculto>"

    display_scheme = parsed.scheme.split("+", 1)[0]
    return f"{display_scheme}://[DIRECT_URL_OCULTA]"


def load_postgres_migrations() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def get_direct_url() -> str:
    direct_url = os.environ.get("DIRECT_URL", "").strip()
    if not direct_url:
        raise RuntimeError("DIRECT_URL ausente. Configure somente no painel/ambiente seguro antes de rodar migrations PostgreSQL.")
    if not is_postgresql_url(direct_url):
        raise RuntimeError(INVALID_DIRECT_URL_MESSAGE)
    parse_direct_url_safely(direct_url)
    return normalize_database_url(direct_url)


def validate_migration_safety() -> None:
    if real_data_mode_enabled():
        raise RuntimeError("Migrations bloqueadas com REAL_DATA_MODE=true nesta fase controlada.")


def split_sql_statements(content: str) -> list[str]:
    return [statement.strip() for statement in content.split(";") if statement.strip()]


def dry_run(migration_paths: list[Path], direct_url: str) -> None:
    print("Dry-run de migrations PostgreSQL.")
    print(f"DIRECT_URL configurada: {mask_database_url(direct_url)}")
    for path in migration_paths:
        print(f"DRY-RUN aplicaria: {path.name}")


def apply_migrations(migration_paths: list[Path], direct_url: str) -> None:
    print("Aplicando migrations PostgreSQL com DIRECT_URL protegida.")
    print(f"DIRECT_URL configurada: {mask_database_url(direct_url)}")
    engine = create_engine(direct_url)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(120) PRIMARY KEY)"))
        applied = {row[0] for row in conn.execute(text("SELECT version FROM schema_migrations")).fetchall()}
        for path in migration_paths:
            if path.name in applied:
                print(f"JA APLICADA: {path.name}")
                continue
            for statement in split_sql_statements(path.read_text(encoding="utf-8")):
                conn.exec_driver_sql(statement)
            conn.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": path.name})
            print(f"APLICADA: {path.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aplica migrations PostgreSQL usando DIRECT_URL sem expor segredos.")
    parser.add_argument("--apply", action="store_true", help="Executa as migrations. Sem esta flag, roda apenas dry-run.")
    args = parser.parse_args(argv)

    validate_migration_safety()
    direct_url = get_direct_url()
    migration_paths = load_postgres_migrations()
    if not migration_paths:
        raise RuntimeError("Nenhuma migration PostgreSQL encontrada.")

    if args.apply:
        apply_migrations(migration_paths, direct_url)
    else:
        dry_run(migration_paths, direct_url)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERRO SEGURO: {exc}", file=sys.stderr)
        raise SystemExit(1)
