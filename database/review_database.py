"""
PatentStructAI Review Database

Database operations for the annotation
and review workflow.

Handles

- reviewed pages
- dataset versions
- review statistics
"""

from sqlalchemy import text

from database.db_connection import (
    get_db
)


# =====================================================
# Database Helpers
# =====================================================

def execute(
    query,
    parameters=None
):

    with get_db() as db:

        return db.execute(
            query,
            parameters or {}
        )


def fetch_all(
    query,
    parameters=None
):

    return execute(
        query,
        parameters
    ).fetchall()


# =====================================================
# Reviewed Pages
# =====================================================

def insert_reviewed_page(
    filename,
    status,
    dataset_version,
    category=None,
    notes=None,
    patent_number=None
):

    query = text("""
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
    """)

    execute(

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

    rows = fetch_all(

        text("""
            SELECT
                filename
            FROM reviewed_pages
        """)

    )

    return {

        row[0]

        for row in rows

    }


def get_reviewed_pages_by_version(
    dataset_version
):

    rows = fetch_all(

        text("""
            SELECT
                filename
            FROM reviewed_pages
            WHERE dataset_version = :dataset_version
        """),

        {
            "dataset_version": dataset_version
        }

    )

    return {

        row[0]

        for row in rows

    }


def get_review_statistics_by_version():

    query = text("""
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
    """)

    return fetch_all(query)


def delete_reviewed_pages(
    filenames
):

    query = text("""
        DELETE FROM reviewed_pages
        WHERE filename = :filename
    """)

    parameters = [

        {
            "filename": filename
        }

        for filename in filenames

    ]

    with get_db() as db:

        db.execute(

            query,

            parameters

        )