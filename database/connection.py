"""Database connection and session management for SalesGenie AI."""

from collections.abc import Generator
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Load environment variables from the project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_required_setting(name: str) -> str:
    """
    Return a required environment variable value.

    Args:
        name: Environment variable name.

    Returns:
        The value of the environment variable.

    Raises:
        RuntimeError: If the environment variable is missing.
    """
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


DATABASE_HOST: str = get_required_setting("DATABASE_HOST")
DATABASE_PORT: int = int(get_required_setting("DATABASE_PORT"))
DATABASE_NAME: str = get_required_setting("DATABASE_NAME")
DATABASE_USER: str = get_required_setting("DATABASE_USER")
DATABASE_PASSWORD: str = get_required_setting("DATABASE_PASSWORD")


DATABASE_URL: URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    database=DATABASE_NAME,
)

# SQLAlchemy engine
engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Database session factory
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session and close it safely after use.
    """
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()
