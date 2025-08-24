from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://krnluser:krnl123@localhost:5432/krnl_onboarding"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("ENVIRONMENT") == "development"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)