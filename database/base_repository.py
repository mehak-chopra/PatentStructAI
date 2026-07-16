"""
Base repository for PatentStructAI.

Provides common database operations shared by all repositories.

Every repository should inherit from BaseRepository instead of
interacting with SQLAlchemy sessions directly.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from database.db_connection import get_db


class BaseRepository:
    """
    Base class for all repositories.

    Child repositories inherit common CRUD helpers while keeping
    SQL isolated inside the database layer.
    """

    TABLE_NAME: Optional[str] = None

    # ------------------------------------------------------------
    # Session Helpers
    # ------------------------------------------------------------

    @staticmethod
    def session():
        """
        Return a managed database session.

        Example
        -------
        with self.session() as db:
            ...
        """
        return get_db()

    # ------------------------------------------------------------
    # Generic Queries
    # ------------------------------------------------------------

    @classmethod
    def count(cls) -> int:
        """
        Return number of rows in the table.
        """

        cls._validate_table()

        with cls.session() as db:

            return db.execute(
                text(
                    f"SELECT COUNT(*) FROM {cls.TABLE_NAME}"
                )
            ).scalar_one()

    @classmethod
    def exists(
        cls,
        column: str,
        value: Any,
    ) -> bool:
        """
        Return True if a row exists.
        """

        cls._validate_table()

        with cls.session() as db:

            result = db.execute(
                text(
                    f"""
                    SELECT 1
                    FROM {cls.TABLE_NAME}
                    WHERE {column} = :value
                    LIMIT 1
                    """
                ),
                {"value": value},
            ).first()

        return result is not None

    @classmethod
    def delete(
        cls,
        column: str,
        value: Any,
    ) -> int:
        """
        Delete rows matching the condition.

        Returns
        -------
        int
            Number of deleted rows.
        """

        cls._validate_table()

        with cls.session() as db:

            result = db.execute(
                text(
                    f"""
                    DELETE
                    FROM {cls.TABLE_NAME}
                    WHERE {column} = :value
                    """
                ),
                {"value": value},
            )

            return result.rowcount

    @classmethod
    def truncate(cls) -> None:
        """
        Remove every row from the table.
        """

        cls._validate_table()

        with cls.session() as db:

            db.execute(
                text(
                    f"TRUNCATE TABLE {cls.TABLE_NAME}"
                )
            )

    @classmethod
    def fetch_all(cls):
        """
        Return every row.

        Child repositories should normally expose richer methods,
        but this helper is useful for debugging.
        """

        cls._validate_table()

        with cls.session() as db:

            result = db.execute(
                text(
                    f"SELECT * FROM {cls.TABLE_NAME}"
                )
            )

            return result.mappings().all()

    @classmethod
    def fetch_one(
        cls,
        column: str,
        value: Any,
    ):
        """
        Fetch a single row.
        """

        cls._validate_table()

        with cls.session() as db:

            result = db.execute(
                text(
                    f"""
                    SELECT *
                    FROM {cls.TABLE_NAME}
                    WHERE {column} = :value
                    LIMIT 1
                    """
                ),
                {"value": value},
            )

            return result.mappings().first()

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    @classmethod
    def _validate_table(cls) -> None:
        """
        Ensure child repositories define TABLE_NAME.
        """

        if cls.TABLE_NAME is None:

            raise ValueError(
                f"{cls.__name__} must define TABLE_NAME."
            )

    # ------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(table='{self.TABLE_NAME}')"
        )