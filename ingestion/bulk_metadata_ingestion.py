from pathlib import Path
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from tqdm import tqdm

from ingestion.metadata_fetcher import (
    fetch_patent_metadata
)

from database.patent_repository import (
    insert_patent,
    insert_failed_patent
)

# change this to the path to the desired patent numbers file
PATENT_FILE = Path(
    "data/chemistry_patent_numbers_v2.txt"
)

MAX_WORKERS = 5


def load_patent_numbers():

    with open(
        PATENT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        patents = [
            line.strip()
            for line in f
            if line.strip()
        ]

    return patents


def process_patent(
    patent_number
):

    try:

        metadata = (
            fetch_patent_metadata(
                patent_number
            )
        )

        insert_patent(
            metadata["patent_number"],
            metadata["title"],
            metadata["pdf_url"],
            metadata["country"]
        )

        return True

    except Exception as e:

        print(
            f"❌ Failed: {patent_number}"
        )

        print(e)

        insert_failed_patent(
            patent_number,
            str(e)
        )
        
        return False


def ingest_patents():

    patents = (
        load_patent_numbers()
    )

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                process_patent,
                patent_number
            )
            for patent_number in patents
        ]

        for _ in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Processing Patents"
        ):
            pass


if __name__ == "__main__":
    ingest_patents()