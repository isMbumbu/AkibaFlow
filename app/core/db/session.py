from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from typing import Generator

# Setup engine with PostgreSQL dialect
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# Setup SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Dependency for API routes to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
