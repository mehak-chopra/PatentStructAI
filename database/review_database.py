from sqlalchemy import text

from database.db_connection import (
    get_db
)


def insert_reviewed_page(
    filename,
    status,
    dataset_version,
    category=None,
    notes=None,
    patent_number=None
):

    query = text(
        """
        INSERT IGNORE INTO reviewed_pages
        (
            filename,
            status,
            category,
            notes,
            patent_number,
            dataset_version
        )
        VALUES
        (
            :filename,
            :status,
            :category,
            :notes,
            :patent_number,
            :dataset_version
        )
        """
    )

    with get_db() as db:

        db.execute(
            query,
            {
                "filename": filename,
                "status": status,
                "category": category,
                "notes": notes,
                "patent_number": patent_number,
                "dataset_version": dataset_version
            }
        )


def get_reviewed_pages():

    with get_db() as db:

        rows = db.execute(
            text(
                """
                SELECT filename
                FROM reviewed_pages
                """
            )
        )

        filenames = {
            row[0]
            for row in rows
        }

    return filenames


def get_reviewed_pages_by_version(
    dataset_version
):

    with get_db() as db:

        rows = db.execute(
            text(
                """
                SELECT filename
                FROM reviewed_pages
                WHERE dataset_version = :dataset_version
                """
            ),
            {
                "dataset_version": dataset_version
            }
        )

        filenames = {
            row[0]
            for row in rows
        }

    return filenames


def get_review_statistics():

    with get_db() as db:

        rows = db.execute(
            text(
                """
                SELECT
                    dataset_version,
                    status,
                    COUNT(*) AS total
                FROM reviewed_pages
                GROUP BY
                    dataset_version,
                    status
                ORDER BY
                    dataset_version,
                    status
                """
            )
        )

        statistics = rows.fetchall()

    return statistics

def delete_reviewed_pages(
    filenames
):

    query = text(
        """
        DELETE FROM reviewed_pages
        WHERE filename = :filename
        """
    )

    with get_db() as db:

        for filename in filenames:

            db.execute(
                query,
                {
                    "filename": filename
                }
            )