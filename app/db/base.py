import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://panel_user:panel_pass@localhost:3308/panel_db",
)

engine = create_engine(
    DATABASE_URL,
    echo=False,          # Set to True during development to log SQL
    pool_pre_ping=True,  # Automatically reconnect on stale connections
    pool_recycle=3600,   # Recycle connections every hour (important for MySQL)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""
    pass


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
