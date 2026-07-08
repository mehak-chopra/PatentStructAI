"""
PatentStructAI Database Connection

Provides:

- SQLAlchemy engine
- Session factory
- Database session context manager
- Database connection test
"""

from contextlib import contextmanager
from urllib.parse import quote_plus
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    Session,
    sessionmaker
)

load_dotenv()

# =====================================================
# Environment Variables
# =====================================================

DB_HOST = os.getenv(
    "DB_HOST"
)

DB_PORT = os.getenv(
    "DB_PORT"
)

DB_USER = os.getenv(
    "DB_USER"
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD"
)

DB_NAME = os.getenv(
    "DB_NAME"
)

required = {

    "DB_HOST":
        DB_HOST,

    "DB_PORT":
        DB_PORT,

    "DB_USER":
        DB_USER,

    "DB_PASSWORD":
        DB_PASSWORD,

    "DB_NAME":
        DB_NAME

}

missing = [

    key

    for key, value in required.items()

    if not value

]

if missing:

    raise RuntimeError(

        "Missing database environment variables:\n"

        + "\n".join(missing)

    )

# =====================================================
# Database Configuration
# =====================================================

DATABASE_URL = (

    "mysql+pymysql://"

    f"{DB_USER}:"

    f"{quote_plus(DB_PASSWORD)}"

    f"@{DB_HOST}:{DB_PORT}"

    f"/{DB_NAME}"

)

engine = create_engine(

    DATABASE_URL,

    pool_pre_ping=True,

    pool_recycle=3600,

    future=True

)

SessionLocal = sessionmaker(

    bind=engine,

    autoflush=False,

    autocommit=False,

    future=True

)

# =====================================================
# Database Session
# =====================================================

@contextmanager
def get_db():

    db: Session = SessionLocal()

    try:

        yield db

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

# =====================================================
# Connection Test
# =====================================================

def test_connection():

    try:

        with engine.connect() as connection:

            connection.execute(

                text("SELECT 1")

            ).scalar()

        print(

            "Database connection successful."

        )

    except Exception as error:

        print(

            "Database connection failed."

        )

        print(

            error

        )


# =====================================================
# Main
# =====================================================

def main():

    test_connection()


if __name__ == "__main__":

    main()