from database.review_database import (
    get_reviewed_pages
)

from pathlib import Path
import random
import shutil

PATENT_FILE = Path(
    "data/chemistry_patent_numbers_v2.txt"
)

EXTRACTED_IMAGES = Path(
    "data/extracted_images"
)

OUTPUT_DIR = Path(
    "annotations/chemistry_raw_pages_v2"
)

CONFIRMED_DIR = Path(
    "annotations/confirmed_chemistry_pages_v2"
)

REJECTED_DIR = Path(
    "annotations/rejected_pages_v2"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CONFIRMED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REJECTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

SAMPLE_SIZE = 300

# this sampler will ONLY sample patents listed in the txt file listed above
def load_patents():

    with open(
        PATENT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        # prevent duplicate patent entries if a patent accidentally pasted twice in the txt file and remove empty lines
        patents = sorted(set(
            line.strip()
            for line in f
            if line.strip()
        ))

    return patents


def collect_pages():

    pages = []

    patents = load_patents()

    print(
        f"Loaded {len(patents)} patents"
    )

    VERBOSE = False

    for patent in patents:

        patent_dir = (
            EXTRACTED_IMAGES /
            patent
        )

        if not patent_dir.exists():

            print(
                f"Missing folder: {patent}"
            )

            continue

        patent_pages = sorted(
            patent_dir.glob("*.png")
        )

        if VERBOSE:
            print(
                f"{patent}: "
                f"{len(patent_pages)} pages"
            )

        pages.extend(
            patent_pages
        )

    return pages

def sample_pages():

    print(
        "\nStarting chemistry page sampling..."
    )

    # clear previous sampling batch.
    # chemistry_raw_pages_v2 is a temporary review folder.
    # move confirmed chemistry pages to
    # annotations/confirmed_chemistry_pages_v2
    # before running the sampler again.

    for file in OUTPUT_DIR.glob(
        "*.png"
    ):
        file.unlink()

    all_pages = collect_pages()

    print(
        f"\nTotal pages collected: "
        f"{len(all_pages)}"
    )

    reviewed_pages = (
        get_reviewed_pages()
    )

    all_page_names = {
        f"{page.parent.name}_{page.name}"
        for page in all_pages
    }

    reviewed_in_corpus = (
        reviewed_pages.intersection(
            all_page_names
        )
    )

    print(
        f"Reviewed pages in current corpus: "
        f"{len(reviewed_in_corpus)}"
    )

    print(
        f"Pages already reviewed "
        f"(database): "
        f"{len(reviewed_pages)}"
    )

    available_pages = [
        page
        for page in all_pages
        if (
            f"{page.parent.name}_{page.name}"
            not in reviewed_pages
        )
    ]

    print(
        f"Unreviewed pages remaining: "
        f"{len(available_pages)}"
    )

    if not available_pages:

        print(
            "No new pages left to sample."
        )

        return

    sample_count = min(
        SAMPLE_SIZE,
        len(available_pages)
    )

    random.shuffle(
        available_pages
    )

    sampled_pages = available_pages[
        :sample_count
    ]

    print(
        f"Sampling {sample_count} pages "
        f"from {len(available_pages)} "
        f"unreviewed pages"
    )

    for page in sampled_pages:

        destination = (
            OUTPUT_DIR /
            f"{page.parent.name}_{page.name}"
        )

        shutil.copy2(
            page,
            destination
        )

    print(
        f"✅ Copied {len(sampled_pages)} pages "
        f"to {OUTPUT_DIR}"
    )

if __name__ == "__main__":
    sample_pages()