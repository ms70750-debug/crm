import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.services.test_database_guard import guard_test_database_url

DATABASE_PATH = Path(__file__).resolve().parents[2] / "app.db"


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if url.startswith("postgresql+psycopg://"):
        parts = urlsplit(url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        query.setdefault("sslmode", "require")
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return url


DATABASE_URL = normalize_database_url(os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}"))
guard_test_database_url(DATABASE_URL, os.environ)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
        max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "5")),
        pool_recycle=int(os.environ.get("DB_POOL_RECYCLE_SECONDS", "1800")),
        pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT_SECONDS", "10")),
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
