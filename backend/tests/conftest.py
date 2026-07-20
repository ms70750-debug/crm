import atexit
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_RUN_ID = os.environ.get("BBB_TEST_RUN_ID", "").strip() or f"pytest-{uuid.uuid4().hex}"
TEST_DB_DIR = Path(tempfile.gettempdir()) / "bbb-consig-crm-tests" / TEST_RUN_ID
TEST_DB_DIR.mkdir(parents=True, exist_ok=True)
TEST_DB_PATH = TEST_DB_DIR / f"{TEST_RUN_ID}.sqlite"
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip() or f"sqlite:///{TEST_DB_PATH.as_posix()}"

os.environ["APP_ENV"] = "test"
os.environ["APP_MODE"] = "demo"
os.environ["REAL_DATA_MODE"] = "false"
os.environ["AUTH_EMAIL_ENABLED"] = "false"
os.environ["AUTH_EMAIL_MODE"] = "simulate"
os.environ["PUBLIC_DEMO_LOGIN_ENABLED"] = "false"
os.environ["BBB_TEST_RUN_ID"] = TEST_RUN_ID
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

for key in (
    "PRIMARY_ADMIN_EMAIL",
    "PRIMARY_ADMIN_PASSWORD",
    "SUPABASE_DIRECT_URL",
    "DIRECT_URL",
    "POSTGRES_RESTORE_URL",
    "RESEND_API_KEY",
    "EVOLUTION_API_TOKEN",
):
    os.environ.pop(key, None)


def _cleanup_test_dir() -> None:
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


atexit.register(_cleanup_test_dir)


import pytest  # noqa: E402
from sqlalchemy import text  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def prepare_application_database():
    from app.database.init_db import init_db
    from app.database.session import Base, engine

    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def isolated_application_database(prepare_application_database):
    from app.database.seed import seed_database
    from app.database.session import Base, SessionLocal, engine
    from app.services.security import _rate_buckets

    _clear_database(Base, engine)
    with SessionLocal() as db:
        seed_database(db)
    _rate_buckets.clear()
    yield
    _rate_buckets.clear()
    _clear_database(Base, engine)


def _clear_database(Base, engine) -> None:
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            tables = ", ".join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
            if tables:
                conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
            return
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
