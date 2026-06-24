from pathlib import Path

from database.review_database import (
    insert_reviewed_page
)


CONFIRMED_DIR = Path(
    "annotations/confirmed_chemistry_pages_v2"
)

REJECTED_DIR = Path(
    "annotations/rejected_pages_v2"
)


def sync_folder(
    folder,
    status
):

    count = 0

    for file in sorted(
        folder.glob("*.png")
    ):

        patent_number = (
            file.stem.rsplit(
                "_page_",
                1
            )[0]
        )

        insert_reviewed_page(
            filename=file.name,
            status=status,
            patent_number=patent_number,
            dataset_version="v2"
        )

        count += 1

    print(
        f"Synced {count} "
        f"{status} pages"
    )


def sync_reviewed_pages():

    sync_folder(
        CONFIRMED_DIR,
        "confirmed"
    )

    sync_folder(
        REJECTED_DIR,
        "rejected"
    )


if __name__ == "__main__":

    sync_reviewed_pages()