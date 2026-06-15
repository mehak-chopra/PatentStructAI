from pathlib import Path
from tqdm import tqdm

from extraction.image_extractor import (
    render_pdf_pages
)

from ingestion.pdf_downloader import (
    download_pdf
)

from database.patent_repository import (
    get_patents_for_processing,
    insert_patent_page,
    mark_pdf_downloaded,
    mark_images_extracted
)


def process_patent(
    patent
):

    try:

        pdf_path = download_pdf(
            patent.id,
            patent.patent_number,
            patent.pdf_url
        )

        if not pdf_path:

            return False

        mark_pdf_downloaded(
            patent.id
        )

        page_records = (
            render_pdf_pages(
                pdf_path,
                patent.patent_number
            )
        )

        for page in page_records:

            insert_patent_page(
                patent.id,
                page["page_number"],
                page["image_path"]
            )

        mark_images_extracted(
            patent.id
        )

        Path(pdf_path).unlink(
            missing_ok=True
        )

        print(
            f"✅ Processed "
            f"{patent.patent_number}"
        )

        return True

    except Exception as e:

        print(
            f"❌ Failed "
            f"{patent.patent_number}"
        )

        print(e)

        return False


def process_all_patents():

    patents = (
        get_patents_for_processing()
    )

    if not patents:

        print(
            "No patents pending."
        )

        return

    for patent in tqdm(
        patents,
        desc="Processing PDFs"
    ):

        process_patent(
            patent
        )


if __name__ == "__main__":
    process_all_patents()