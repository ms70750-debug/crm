from pathlib import Path

from sqlalchemy import text

from app.database.seed import seed_database
from app.database.session import Base, DATABASE_URL, SessionLocal, engine
from app import models  # noqa: F401


def apply_migrations() -> None:
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR(120) PRIMARY KEY)"))
        applied = {row[0] for row in conn.execute(text("SELECT version FROM schema_migrations")).fetchall()}

        if not DATABASE_URL.startswith("sqlite"):
            for path in sorted(migrations_dir.glob("*.sql")):
                if path.name not in applied:
                    conn.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": path.name})
            return

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
            conn.execute(text("INSERT INTO schema_migrations (version) VALUES (:version)"), {"version": path.name})


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    apply_migrations()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
