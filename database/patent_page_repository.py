"""
Patent page repository for PatentStructAI.

Responsible for all operations involving the patent_pages table.

This repository intentionally does NOT manage:

- patents
- structures

Those are handled by their own repositories.
"""

from __future__ import annotations

from sqlalchemy import text

from database.base_repository import BaseRepository
from database.models import PatentPageRecord


# =====================================================
# Patent Page Repository
# =====================================================

class PatentPageRepository(BaseRepository):
    """
    Repository responsible for all operations on the
    patent_pages table.
    """

    TABLE_NAME = "patent_pages"

    # ------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------

    @classmethod
    def save(
        cls,
        page: PatentPageRecord,
    ) -> None:
        """
        Insert one patent page.

        Duplicate (patent_id, page_number) rows are ignored.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    INSERT IGNORE INTO patent_pages
                    (
                        patent_id,
                        page_number,
                        image_path
                    )
                    VALUES
                    (
                        :patent_id,
                        :page_number,
                        :image_path
                    )
                    """
                ),

                {
                    "patent_id": page.patent_id,
                    "page_number": page.page_number,
                    "image_path": page.image_path,
                },

            )


    @classmethod
    def save_many(
        cls,
        pages: list[PatentPageRecord],
    ) -> None:
        """
        Insert multiple rendered pages.
        """

        for page in pages:

            cls.save(page)

    # ------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------

    @classmethod
    def update_classification(
        cls,
        page_id: int,
        contains_chemistry: bool | None,
        chemistry_score: float | None,
    ) -> None:
        """
        Store page classification results.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE patent_pages
                    SET
                        contains_chemistry = :contains_chemistry,
                        chemistry_score = :chemistry_score
                    WHERE id = :page_id
                    """
                ),

                {
                    "page_id": page_id,
                    "contains_chemistry": contains_chemistry,
                    "chemistry_score": chemistry_score,
                },

            )

    # ------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------

    @classmethod
    def get(
        cls,
        page_id: int,
    ):

        return cls.fetch_one(
            "id",
            page_id,
        )


    @classmethod
    def get_by_patent(
        cls,
        patent_id: int,
    ):
        """
        Return every page belonging to a patent.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patent_pages
                    WHERE patent_id = :patent_id
                    ORDER BY page_number
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )

            return result.mappings().all()


    @classmethod
    def chemistry_pages(
        cls,
        patent_id: int,
    ):
        """
        Return only chemistry pages.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patent_pages
                    WHERE
                        patent_id = :patent_id
                        AND contains_chemistry = TRUE
                    ORDER BY page_number
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )

            return result.mappings().all()


    @classmethod
    def uncertain_pages(
        cls,
        patent_id: int,
    ):
        """
        Return pages whose classification is unknown.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patent_pages
                    WHERE
                        patent_id = :patent_id
                        AND contains_chemistry IS NULL
                    ORDER BY page_number
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )

            return result.mappings().all()

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    @classmethod
    def count_chemistry_pages(
        cls,
    ) -> int:
        """
        Return the number of chemistry pages.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM patent_pages
                    WHERE contains_chemistry = TRUE
                    """
                )

            ).scalar_one()


    @classmethod
    def count_non_chemistry_pages(
        cls,
    ) -> int:
        """
        Return the number of non-chemistry pages.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM patent_pages
                    WHERE contains_chemistry = FALSE
                    """
                )

            ).scalar_one()


    @classmethod
    def count_uncertain_pages(
        cls,
    ) -> int:
        """
        Return pages that have not yet been classified.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM patent_pages
                    WHERE contains_chemistry IS NULL
                    """
                )

            ).scalar_one()


    @classmethod
    def average_pages_per_patent(
        cls,
    ) -> float:
        """
        Average rendered pages per patent.
        """

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT
                        AVG(page_count)
                    FROM
                    (
                        SELECT
                            patent_id,
                            COUNT(*) AS page_count
                        FROM patent_pages
                        GROUP BY patent_id
                    ) AS page_statistics
                    """
                )

            ).scalar_one()

    # ------------------------------------------------------------
    # Sampling Utilities
    # ------------------------------------------------------------

    @classmethod
    def random_pages(
        cls,
        limit: int,
    ):
        """
        Return random page images.

        Used by annotation dataset generation.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT
                        id,
                        image_path
                    FROM patent_pages
                    ORDER BY RAND()
                    LIMIT :limit
                    """
                ),

                {
                    "limit": limit,
                },

            )

            return result.mappings().all()


    @classmethod
    def all_pages(
        cls,
    ):
        """
        Return every rendered page.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT
                        *
                    FROM patent_pages
                    ORDER BY patent_id,
                            page_number
                    """
                )

            )

            return result.mappings().all()