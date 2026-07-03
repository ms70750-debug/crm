import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import create_engine, text

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.environment import is_postgresql_url, real_data_mode_enabled  # noqa: E402
from app.database.session import normalize_database_url  # noqa: E402

MIGRATIONS_DIR = BACKEND_ROOT / "migrations" / "postgres"


def mask_database_url(database_url: str) -> str:
    parsed = urlsplit(database_url)
    if not parsed.netloc:
        return "<valor oculto>"

    host = parsed.hostname or "host"
    port = f":{parsed.port}" if parsed.port else ""
    user = parsed.username or "usuario"
    masked_netloc = f"{user}:***@{host}{port}"
    return urlunsplit((parsed.scheme, masked_netloc, parsed.path, "", ""))


def load_postgres_migrations() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def get_direct_url() -> str:
    direct_url = os.environ.get("DIRECT_URL", "").strip()
    if not direct_url:
        raise RuntimeError("DIRECT_URL ausente. Configure somente no painel/ambiente seguro antes de rodar migrations PostgreSQL.")
    if not is_postgresql_url(direct_url):
        raise RuntimeError("DIRECT_URL deve apontar para PostgreSQL/Supabase.")
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
    raise SystemExit(main())
