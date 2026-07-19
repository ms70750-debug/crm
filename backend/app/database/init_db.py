import logging
import os
from pathlib import Path

from sqlalchemy import text

from app.database.seed import ensure_primary_admin_from_env, seed_database
from app.database.session import Base, DATABASE_URL, SessionLocal, engine
from app import models  # noqa: F401

logger = logging.getLogger("bbb-consig.database")
PRODUCTION_ENV_VALUES = {"production", "prod", "render"}


def is_sqlite_database() -> bool:
    return DATABASE_URL.startswith("sqlite")


def should_auto_bootstrap_schema() -> bool:
    app_env = os.environ.get("APP_ENV", "local").strip().lower()
    return app_env not in PRODUCTION_ENV_VALUES


def apply_migrations() -> None:
    migrations_root = Path(__file__).resolve().parents[2] / "migrations"
    migrations_dir = migrations_root / ("sqlite" if is_sqlite_database() else "postgres")
    migration_paths = sorted(migrations_dir.glob("*.sql"))
    if is_sqlite_database():
        migration_paths = sorted(migrations_root.glob("*.sql")) + migration_paths
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(120) PRIMARY KEY)"))
        applied = {row[0] for row in conn.execute(text("SELECT version FROM schema_migrations")).fetchall()}

        if not should_auto_bootstrap_schema():
            logger.warning("Migrations PostgreSQL devem ser aplicadas formalmente antes do uso real; bootstrap automatico bloqueado.")
            for path in migration_paths:
                if path.name not in applied:
                    conn.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": path.name})
            return

        for path in migration_paths:
            if path.name in applied:
                continue
            statements = [stmt.strip() for stmt in path.read_text(encoding="utf-8").split(";") if stmt.strip()]
            for statement in statements:
                try:
                    conn.exec_driver_sql(statement)
                except Exception as exc:
                    message = str(exc).lower()
                    if "duplicate column" not in message and "already exists" not in message:
                        raise
            conn.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": path.name})


def init_db() -> None:
    if not should_auto_bootstrap_schema():
        logger.warning("Base.metadata.create_all nao e estrategia de producao real; inicializacao automatica de schema ignorada.")
        db = SessionLocal()
        try:
            ensure_primary_admin_from_env(db)
        finally:
            db.close()
        return

    Base.metadata.create_all(bind=engine)
    apply_migrations()
    db = SessionLocal()
    try:
        seed_database(db)
        ensure_primary_admin_from_env(db)
    finally:
        db.close()
