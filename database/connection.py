"""
database/connection.py
Central PostgreSQL connection for the whole SalesGenie AI project.
All modules (module1..module6) should import get_db / SessionLocal from here
so everyone shares ONE connection pool instead of opening their own.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/salesgenie",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema_columns():
    """Add any missing columns to already-created tables so older databases can run newer models."""
    from database import models  # noqa: F401  (ensures models are registered)

    inspector = inspect(engine)
    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            table.create(bind=engine)
            continue

        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        for column in table.columns:
            if column.name in existing_columns:
                continue

            column_type = column.type.compile(dialect=engine.dialect)
            statement = f'ALTER TABLE "{table_name}" ADD COLUMN "{column.name}" {column_type}'
            with engine.begin() as connection:
                connection.execute(text(statement))


def init_db():
    """
    Creates all tables that don't exist yet and upgrades existing ones with any
    missing columns required by the current ORM models.
    """
    from database import models  # noqa: F401  (ensures models are registered)
    Base.metadata.create_all(bind=engine)
    ensure_schema_columns()
