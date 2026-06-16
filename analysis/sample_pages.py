from pathlib import Path
import shutil

from database.patent_repository import (
    get_random_pages
)

for file in OUTPUT_DIR.glob("*"):

    if file.is_file():

        file.unlink()
OUTPUT_DIR = Path(
    "annotations/raw_pages"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def sample_pages(
    sample_size=100
):

    pages = (
        get_random_pages(
            sample_size
        )
    )

    copied = 0

    for row in pages:

        source = Path(
            row.image_path
        )

        if not source.exists():
            continue

        patent_folder = (
            source.parent.name
        )

        destination = (
            OUTPUT_DIR /
            f"{patent_folder}_{source.name}"
        )

        shutil.copy2(
            source,
            destination
        )

        copied += 1

    print(
        f"✅ Copied "
        f"{copied} pages"
    )


if __name__ == "__main__":

    sample_pages(
        sample_size=100
    )