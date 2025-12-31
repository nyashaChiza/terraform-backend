from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# -----------------------------
# DATABASE URL CONFIGURATION
# -----------------------------
# Example PostgreSQL URL: postgresql+psycopg2://user:password@localhost:5432/gymtrack
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

# -----------------------------
# ENGINE CREATION
# -----------------------------
# For PostgreSQL, replace the URL with the actual connection string
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# -----------------------------
# SESSION FACTORY
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# DEPENDENCY FOR FASTAPI
# -----------------------------
# Usage in FastAPI endpoints:
# from db.session import SessionLocal
# db = Depends(get_db)
def get_db():
    """
    Yield a database session for FastAPI routes.
    Ensures proper commit/rollback and closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
