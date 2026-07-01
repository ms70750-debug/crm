from app.database.seed import seed_database
from app.database.session import Base, SessionLocal, engine
from app import models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
