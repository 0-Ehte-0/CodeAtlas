# apps/api/database.py
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Database connection URL targeting the PostgreSQL Docker container
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://codeatlas:codeatlas@localhost:5432/codeatlas"
)

# Initialize SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Checks connection health prior to executing queries to prevent stale connection errors
)

# Session factory for generating scoped database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a transactional SQLAlchemy session per request.
    Automatically closes the session in the 'finally' block once the request completes,
    preventing database connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()