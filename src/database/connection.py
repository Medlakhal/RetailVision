import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine


# Project root: C:\RetailVision
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables from the .env file
load_dotenv(PROJECT_ROOT / ".env")


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for the RetailVision PostgreSQL database."""

    required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing_vars = [name for name in required_vars if not os.getenv(name)]

    if missing_vars:
        raise ValueError(
            f"Missing environment variables in .env: {', '.join(missing_vars)}"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(database_url, pool_pre_ping=True)


def test_connection() -> None:
    """Test the PostgreSQL connection without exposing credentials."""

    engine = get_engine()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Connexion PostgreSQL réussie !")
    finally:
        engine.dispose()