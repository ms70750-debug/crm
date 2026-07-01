from pathlib import Path

from app.database.seed import seed_database
from app.database.session import Base, SessionLocal, engine
from app import models  # noqa: F401


def apply_migrations() -> None:
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(120) PRIMARY KEY)")
        applied = {row[0] for row in conn.exec_driver_sql("SELECT version FROM schema_migrations").fetchall()}
        for path in sorted(migrations_dir.glob("*.sql")):
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
            conn.exec_driver_sql("INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)", (path.name,))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    apply_migrations()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
