from sqlalchemy import text
from database.db_connection import engine


def insert_patent(
    patent_number,
    title,
    pdf_url,
    country
):
    # wont create duplicates due to IGNORE,
    # but will log if it fails for other reasons

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

        with engine.begin() as conn:

            conn.execute(
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

    except Exception as e:

        print(
            f"❌ Failed {patent_number}"
        )

        print(e)


def get_pending_patents():

    query = text("""
        SELECT
            id,
            patent_number,
            pdf_url
        FROM patents
        WHERE pdf_downloaded = FALSE
            AND pdf_url IS NOT NULL
    """)

    with engine.begin() as conn:

        result = conn.execute(query)

        return result.fetchall()


def mark_pdf_downloaded(
    patent_id
):

    query = text("""
        UPDATE patents
        SET pdf_downloaded = TRUE
        WHERE id = :patent_id
    """)

    with engine.begin() as conn:

        conn.execute(
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

    with engine.begin() as conn:

        conn.execute(
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

    with engine.begin() as conn:

        conn.execute(
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
        WHERE images_extracted = FALSE
            AND pdf_available = TRUE
            AND pdf_url IS NOT NULL
    """)

    with engine.begin() as conn:

        result = conn.execute(query)

        return result.fetchall()


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

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {
                "patent_id": patent_id
            }
        )

        return result.fetchall()
    
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

    with engine.begin() as conn:

        conn.execute(
            query,
            {
                "patent_number":
                    patent_number,

                "error_message":
                    error_message
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

    with engine.begin() as conn:

        result = conn.execute(query)

        return result.fetchall()
    
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

    with engine.begin() as conn:

        conn.execute(
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

    with engine.begin() as conn:

        result = conn.execute(
            query,
            {
                "limit": limit
            }
        )

        return result.fetchall()
    
def get_all_patent_pages():

    query = text("""
        SELECT
            id,
            image_path
        FROM patent_pages
    """)

    with engine.begin() as conn:

        result = conn.execute(query)

        return result.fetchall()


def update_page_triage(
    page_id,
    chemistry_score,
    contains_chemistry
):

    query = text("""
        UPDATE patent_pages
        SET
            chemistry_score = :chemistry_score,
            contains_chemistry = :contains_chemistry
        WHERE id = :page_id
    """)

    with engine.begin() as conn:

        conn.execute(
            query,
            {
                "page_id": page_id,
                "chemistry_score": chemistry_score,
                "contains_chemistry": contains_chemistry
            }
        )