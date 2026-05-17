from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

try:
    # when running from project root
    from backend.config.settings import DATABASE_URL
except Exception:
    # when running from backend folder
    from config.settings import DATABASE_URL


def _is_sqlite(db_url: str) -> bool:
    return db_url.startswith("sqlite:")


connect_args = {"check_same_thread": False} if _is_sqlite(DATABASE_URL) else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

