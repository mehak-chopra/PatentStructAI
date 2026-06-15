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