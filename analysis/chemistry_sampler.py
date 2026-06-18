from pathlib import Path
import random
import shutil

PATENT_FILE = Path(
    "data/chemistry_patent_numbers.txt"
)

EXTRACTED_IMAGES = Path(
    "data/extracted_images"
)

OUTPUT_DIR = Path(
    "annotations/chemistry_raw_pages"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SAMPLE_SIZE = 150


def load_patents():

    with open(
        PATENT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return [
            line.strip()
            for line in f
            if line.strip()
        ]


def collect_pages():

    pages = []

    patents = load_patents()

    print(f"Loaded {len(patents)} patents")

    for patent in patents:

        patent_dir = (
            EXTRACTED_IMAGES /
            patent
        )

        print(
            f"Checking: {patent_dir}"
        )

        if not patent_dir.exists():

            print(
                f"Missing folder: {patent}"
            )

            continue

        patent_pages = list(
            patent_dir.glob("*.png")
        )

        print(
            f"{patent}: "
            f"{len(patent_pages)} pages"
        )

        pages.extend(
            patent_pages
        )

    return pages


def sample_pages():

# clear previous sampling batch.
# chemistry_raw_pages is a temporary review folder.
# confirmed chemistry pages must be moved to
# annotations/confirmed_chemistry_pages
# before running the sampler again.

    for file in OUTPUT_DIR.glob(
        "*.png"
    ):
        file.unlink()
        
    pages = collect_pages()

    if not pages:

        print(
            "No pages found."
        )

        return

    sample_count = min(
        SAMPLE_SIZE,
        len(pages)
    )

    sampled_pages = random.sample(
        pages,
        sample_count
    )

    copied = 0

    for page in sampled_pages:

        destination = (
            OUTPUT_DIR /
            f"{page.parent.name}_{page.name}"
        )

        shutil.copy2(
            page,
            destination
        )

        copied += 1

    print(
        f"✅ Copied "
        f"{copied} chemistry pages"
    )


if __name__ == "__main__":
    sample_pages()