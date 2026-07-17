from database.review_database import (
    delete_reviewed_pages,
    get_reviewed_pages
)

from analysis.sample_annotation_pages import (
    collect_pages
)


def cleanup_review_database():

    reviewed_pages = get_reviewed_pages()

    all_pages = collect_pages()

    all_page_names = {
        f"{page.parent.name}_{page.name}"
        for page in all_pages
    }

    orphan_pages = (
        reviewed_pages -
        all_page_names
    )

    print(
        f"Orphan pages found: "
        f"{len(orphan_pages)}"
    )

    if not orphan_pages:

        print(
            "Database is clean."
        )

        return

    delete_reviewed_pages(
        orphan_pages
    )

    print(
        f"Deleted {len(orphan_pages)} orphan pages."
    )


if __name__ == "__main__":

    cleanup_review_database()
