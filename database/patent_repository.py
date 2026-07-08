"""
PatentStructAI Patent Repository

Contains all database operations for

- Patent metadata
- Patent pages
- Processing status
- Dataset statistics
- Sampling utilities
"""

from sqlalchemy import text

from database.db_connection import engine


# =====================================================
# Database Helpers
# =====================================================

def execute(
    query,
    parameters=None
):

    with engine.begin() as conn:

        return conn.execute(
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


def fetch_one(
    query,
    parameters=None
):

    return execute(
        query,
        parameters
    ).first()


def fetch_scalar(
    query,
    parameters=None
):

    return execute(
        query,
        parameters
    ).scalar()


# =====================================================
# Patent Insertion
# =====================================================

def insert_patent(
    patent_number,
    title,
    pdf_url,
    country
):

    query = text("""
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
    """)

    try:

        execute(

            query,

            {
                "patent_number": patent_number,
                "title": title,
                "pdf_url": pdf_url,
                "country": country
            }

        )

        print(
            f"✅ Stored {patent_number}"
        )

    except Exception as error:

        print(
            f"❌ Failed {patent_number}"
        )

        print(error)


def get_pending_patents():

    query = text("""
        SELECT
            id,
            patent_number,
            pdf_url
        FROM patents
        WHERE
            pdf_downloaded = FALSE
            AND pdf_url IS NOT NULL
    """)

    return fetch_all(query)


def mark_pdf_downloaded(
    patent_id
):

    query = text("""
        UPDATE patents
        SET pdf_downloaded = TRUE
        WHERE id = :patent_id
    """)

    execute(

        query,

        {
            "patent_id": patent_id
        }

    )


def mark_images_extracted(
    patent_id
):

    query = text("""
        UPDATE patents
        SET images_extracted = TRUE
        WHERE id = :patent_id
    """)

    execute(

        query,

        {
            "patent_id": patent_id
        }

    )


def insert_patent_page(
    patent_id,
    page_number,
    image_path
):

    query = text("""
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
    """)

    execute(

        query,

        {
            "patent_id": patent_id,
            "page_number": page_number,
            "image_path": image_path
        }

    )


def get_patents_for_processing():

    query = text("""
        SELECT
            id,
            patent_number,
            pdf_url
        FROM patents
        WHERE
            images_extracted = FALSE
            AND pdf_available = TRUE
            AND pdf_url IS NOT NULL
    """)

    return fetch_all(query)


def get_patent_pages(
    patent_id
):

    query = text("""
        SELECT
            id,
            page_number,
            image_path
        FROM patent_pages
        WHERE patent_id = :patent_id
        ORDER BY page_number
    """)

    return fetch_all(

        query,

        {
            "patent_id": patent_id
        }

    )

def insert_failed_patent(
    patent_number,
    error_message
):

    query = text("""
        INSERT IGNORE INTO failed_patents
        (
            patent_number,
            error_message
        )
        VALUES
        (
            :patent_number,
            :error_message
        )
    """)

    execute(

        query,

        {
            "patent_number": patent_number,
            "error_message": error_message
        }

    )


def get_failed_patents():

    query = text("""
        SELECT
            patent_number,
            error_message,
            failed_at
        FROM failed_patents
    """)

    return fetch_all(query)


def get_patent_count():

    query = text("""
        SELECT COUNT(*)
        FROM patents
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()


def get_page_count():

    query = text("""
        SELECT COUNT(*)
        FROM patent_pages
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()


def get_failed_patent_count():

    query = text("""
        SELECT COUNT(*)
        FROM failed_patents
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()


def get_country_stats():

    query = text("""
        SELECT
            country,
            COUNT(*) AS total
        FROM patents
        GROUP BY country
        ORDER BY total DESC
    """)

    with engine.begin() as conn:

        result = conn.execute(query)

        return result.fetchall()


def get_average_pages_per_patent():

    query = text("""
        SELECT
            AVG(page_count)
        FROM
        (
            SELECT
                patent_id,
                COUNT(*) AS page_count
            FROM patent_pages
            GROUP BY patent_id
        ) t
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()
    

def mark_pdf_unavailable(
    patent_id
):

    query = text("""
        UPDATE patents
        SET pdf_available = FALSE
        WHERE id = :patent_id
    """)

    execute(

        query,

        {
            "patent_id": patent_id
        }

    )

def get_no_pdf_count():

    query = text("""
        SELECT COUNT(*)
        FROM patents
        WHERE pdf_available = FALSE
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()
    
def get_no_pdf_count():

    query = text("""
        SELECT COUNT(*)
        FROM patents
        WHERE pdf_available = FALSE
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()


def get_processed_patent_count():

    query = text("""
        SELECT COUNT(*)
        FROM patents
        WHERE images_extracted = TRUE
    """)

    with engine.begin() as conn:

        return conn.execute(
            query
        ).scalar()


def get_random_pages(
    limit
):

    query = text("""
        SELECT
            image_path
        FROM patent_pages
        ORDER BY RAND()
        LIMIT :limit
    """)

    return fetch_all(

        query,

        {
            "limit": limit
        }

    )


def get_all_patent_pages():

    query = text("""
        SELECT
            id,
            image_path
        FROM patent_pages
    """)

    return fetch_all(query)
