"""
Patent repository for PatentStructAI.

Responsible for all operations involving:

- patents
- failed_patents

This repository intentionally does NOT manage:

- patent_pages
- structures

Those are handled by their own repositories.
"""

from __future__ import annotations

from sqlalchemy import text

from database.base_repository import BaseRepository
from database.models import PatentRecord


# =====================================================
# Patent Repository
# =====================================================

class PatentRepository(BaseRepository):
    """
    Repository responsible for all operations on the
    patents and failed_patents tables.
    """

    TABLE_NAME = "patents"

    # =====================================================
    # Patent Insertion
    # =====================================================

    @classmethod
    def save(
        cls,
        patent: PatentRecord,
    ) -> None:
        """
        Insert a patent if it does not already exist.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    INSERT IGNORE INTO patents
                    (
                        patent_number,
                        title,
                        pdf_url,
                        country
                    )
                    VALUES
                    (
                        :patent_number,
                        :title,
                        :pdf_url,
                        :country
                    )
                    """
                ),

                {
                    "patent_number": patent.patent_number,
                    "title": patent.title,
                    "pdf_url": patent.pdf_url,
                    "country": patent.country,
                },

            )

    @classmethod
    def pending_downloads(cls):
        """
        Return patents whose PDFs have not yet been downloaded.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT
                        *
                    FROM patents
                    WHERE
                        pdf_downloaded = FALSE
                        AND pdf_url IS NOT NULL
                    """
                )

            )

            return result.mappings().all()

    @classmethod
    def pending_processing(cls):
        """
        Return patents ready for page extraction.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patents
                    WHERE
                        images_extracted = FALSE
                        AND pdf_available = TRUE
                        AND pdf_url IS NOT NULL
                    """
                )

            )

            return result.mappings().all()

    # ------------------------------------------------------------
    # Status Updates
    # ------------------------------------------------------------

    @classmethod
    def mark_downloaded(
        cls,
        patent_id,
        local_pdf_path,
        file_size,
        download_duration,
    ):

        with cls.session() as db:
            db.execute(
                text(
                    """
                    UPDATE patents
                    SET
                        pdf_downloaded = TRUE,
                        local_pdf_path = :local_pdf_path,
                        file_size = :file_size,
                        download_at = NOW(),
                        download_duration = :download_duration
                    WHERE
                        id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                    "local_pdf_path": local_pdf_path,
                    "file_size": file_size,
                    "download_duration": download_duration,
                }
            )


    @classmethod
    def mark_images_extracted(
        cls,
        patent_id: int,
    ) -> None:
        """
        Mark rendered page extraction as complete.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE patents
                    SET images_extracted = TRUE
                    WHERE id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )


    @classmethod
    def mark_structures_extracted(
        cls,
        patent_id: int,
    ) -> None:
        """
        Mark chemistry extraction as complete.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE patents
                    SET structures_extracted = TRUE
                    WHERE id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )


    @classmethod
    def mark_processed(
        cls,
        patent_id,
    ):

        with cls.session() as db:
            db.execute(
                text(
                    """
                    UPDATE patents
                    SET
                        processed = TRUE,
                        processed_at = NOW()
                    WHERE
                        id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                }
            )


    @classmethod
    def mark_pdf_unavailable(
        cls,
        patent_id: int,
    ) -> None:
        """
        Mark patents whose PDF is unavailable.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE patents
                    SET pdf_available = FALSE
                    WHERE id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                },

            )

    # ------------------------------------------------------------
    # Failed Patents
    # ------------------------------------------------------------

    @classmethod
    def save_failure(
        cls,
        patent_number: str,
        error_message: str,
        failure_stage: str = "unknown",
    ) -> None:
        """
        Store a failed patent import.
        """

        with cls.session() as db:

            db.execute(

                text(
                    """
                    INSERT IGNORE INTO failed_patents
                    (
                        patent_number,
                        failure_stage,
                        error_message,
                        retry_count
                    )
                    VALUES
                    (
                        :patent_number,
                        :failure_stage,
                        :error_message,
                        0
                    )
                    """
                ),

                {
                    "patent_number": patent_number,
                    "error_message": error_message,
                    "failure_stage": failure_stage,
                },

            )


    @classmethod
    def failed_patents(cls):
        """
        Return every failed patent.
        """

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM failed_patents
                    ORDER BY created_at DESC
                    """
                )

            )

            return result.mappings().all()

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    @classmethod
    def processed_count(cls) -> int:

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM patents
                    WHERE processed = TRUE
                    """
                )

            ).scalar_one()


    @classmethod
    def unavailable_pdf_count(cls) -> int:

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM patents
                    WHERE pdf_available = FALSE
                    """
                )

            ).scalar_one()


    @classmethod
    def failed_count(cls) -> int:

        with cls.session() as db:

            return db.execute(

                text(
                    """
                    SELECT COUNT(*)
                    FROM failed_patents
                    """
                )

            ).scalar_one()


    @classmethod
    def country_statistics(cls):

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT
                        country,
                        COUNT(*) AS total
                    FROM patents
                    GROUP BY country
                    ORDER BY total DESC
                    """
                )

            )

            return result.mappings().all()

    # ------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------

    @classmethod
    def get_by_number(
        cls,
        patent_number: str,
    ):

        return cls.fetch_one(
            "patent_number",
            patent_number,
        )


    @classmethod
    def exists(
        cls,
        patent_number: str,
    ) -> bool:

        return super().exists(
            "patent_number",
            patent_number,
        )
    

    @classmethod
    def pending_metadata(cls):

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patents
                    WHERE
                        pdf_url IS NULL
                    ORDER BY id
                    """
                )

            )

            return result.mappings().all()


    @classmethod
    def pending_pipeline(cls):

        with cls.session() as db:

            result = db.execute(

                text(
                    """
                    SELECT *
                    FROM patents
                    WHERE

                        processed = FALSE

                        AND

                        pdf_available = TRUE

                        AND

                        pdf_url IS NOT NULL

                    ORDER BY id
                    """
                )

            )

            return result.mappings().all()
        
    @classmethod
    def mark_download_failed(

        cls,

        patent_id,

        error,

    ):

        with cls.session() as db:

            db.execute(

                text(
                    """
                    UPDATE patents
                    SET

                        pdf_available = FALSE,

                        download_error = :error

                    WHERE

                        id = :patent_id
                    """
                ),

                {

                    "patent_id": patent_id,

                    "error": error,

                }

            )

    @classmethod
    def mark_processing_started(
        cls,
        patent_id,
    ):

        with cls.session() as db:
            db.execute(
                text(
                    """
                    UPDATE patents
                    SET
                        processing_started_at = NOW()
                    WHERE
                        id = :patent_id
                    """
                ),

                {
                    "patent_id": patent_id,
                }
            )