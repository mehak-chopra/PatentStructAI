"""
PatentStructAI Complete Patent Pipeline

Workflow
--------

Patent Numbers TXT
        │
        ▼
Fetch Google Patent Metadata
        │
        ▼
Store Metadata in Database
        │
        ▼
Download Patent PDF
        │
        ▼
Run Patent Processing Pipeline
        │
        ▼
Store Searchable Structures
        │
        ▼
Cleanup Temporary Files

Example
-------

python -m pipeline.patent_pipeline

Optional

python -m pipeline.patent_pipeline `
    --patent-file data/chemistry_patent_numbers_v2.txt

"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from tqdm import tqdm

from ingestion.metadata_fetcher import (
    fetch_patent_metadata,
)

from ingestion.pdf_downloader import (
    download_pdf,
)

from pipeline.process_patent import (
    PatentPipeline,
)

from database.models import (
    PatentRecord,
)

from database.patent_repository import (
    PatentRepository,
)

# ============================================================
# Project Paths
# ============================================================

PROJECT_ROOT = Path(".")

DATA_ROOT = (
    PROJECT_ROOT /
    "data"
)

TEMP_ROOT = (
    DATA_ROOT /
    "temp"
)

OUTPUT_ROOT = (
    PROJECT_ROOT /
    "outputs"
)

DEFAULT_PATENT_FILE = (
    DATA_ROOT /
    "chemistry_patent_numbers_v2.txt"
)

TEMP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)

# ============================================================
# Validation
# ============================================================

def validate(
    patent_file: Path,
) -> None:
    """
    Validate pipeline inputs.
    """

    if not patent_file.exists():

        raise FileNotFoundError(

            f"Patent list not found:\n{patent_file}"

        )

# ============================================================
# Complete Patent Pipeline
# ============================================================

class PatentPipelineRunner:
    """
    Complete production pipeline.

    Responsibilities

    1. Read patent numbers

    2. Fetch metadata

    3. Store metadata

    4. Download PDFs

    5. Execute PatentPipeline

    6. Update database

    7. Cleanup

    8. Produce summary
    """

    def __init__(
        self,
        patent_file: Path,
        classifier: str,
        detector: str,
        device: str,
        classifier_confidence: float,
        detector_confidence: float,
        padding: int,
    ):

        self.patent_file = Path(
            patent_file
        )

        self.classifier = classifier

        self.detector = detector

        self.device = device

        self.classifier_confidence = (
            classifier_confidence
        )

        self.detector_confidence = (
            detector_confidence
        )

        self.padding = padding

        self.repository = PatentRepository()

        self.total_patents = 0

        self.metadata_added = 0

        self.downloaded = 0

        self.processed = 0

        self.metadata_skipped = 0

        self.failed = []

        validate(
            self.patent_file
        )

        print()

        print("=" * 60)

        print(
            "PatentStructAI Complete Patent Pipeline"
        )

        print("=" * 60)

        print()

        print(
            f"Patent List : {self.patent_file}"
        )

        print(
            f"Classifier  : {self.classifier}"
        )

        print(
            f"Detector    : {self.detector}"
        )

        print(
            f"Device      : {self.device}"
        )

        print()


    # =================================================
    # Load Patent Numbers
    # =================================================

    def load_patent_numbers(self) -> list[str]:
        """
        Read patent numbers from the configured TXT file.
        """

        with open(
            self.patent_file,
            "r",
            encoding="utf-8",
        ) as file:

            patents = [

                line.strip()

                for line in file

                if line.strip()

            ]

        self.total_patents = len(
            patents
        )

        print(

            f"Loaded {self.total_patents} patent numbers."

        )

        print()

        return patents


    # =================================================
    # Save Metadata
    # =================================================

    def save_metadata(
        self,
        metadata: dict,
    ) -> None:
        """
        Store patent metadata in the database.

        Existing patents are ignored automatically by
        PatentRepository.save().
        """

        patent = PatentRecord(

            patent_number=metadata["patent_number"],

            title=metadata["title"],

            pdf_url=metadata["pdf_url"],

            country=metadata["country"],

        )

        if self.repository.exists(
            patent.patent_number
        ):

            self.metadata_skipped += 1

            return

        self.repository.save(patent)

        self.metadata_added += 1


    # =================================================
    # Fetch Metadata
    # =================================================

    def fetch_and_store_metadata(self) -> None:
        """
        Fetch Google Patent metadata for every patent
        listed in the TXT file.
        """

        print("=" * 60)

        print("Step 1 : Fetch Patent Metadata")

        print("=" * 60)

        print()

        patents = self.load_patent_numbers()

        for patent_number in tqdm(

            patents,

            desc="Metadata",

            unit="patent",

        ):

            try:

                metadata = fetch_patent_metadata(

                    patent_number

                )

                self.save_metadata(
                    metadata
                )

            except Exception as error:

                print()

                print(

                    f"Failed : {patent_number}"

                )

                print(error)

                print()

                self.failed.append(

                    {

                        "patent": patent_number,

                        "stage": "metadata",

                        "error": str(error),

                    }

                )

                self.repository.save_failure(

                    patent_number=patent_number,

                    error_message=str(error),

                    failure_stage="metadata",

                )

        print()

        print(

            f"Metadata Stored : {self.metadata_added}"

        )

        print()


    # =================================================
    # Pending Patents
    # =================================================

    def pending_patents(
        self,
    ):
        """
        Return patents waiting to be processed.
        """

        return self.repository.pending_pipeline()


    # =================================================
    # Download PDF
    # =================================================

    # =================================================
    # Download PDF
    # =================================================

    def download_patent_pdf(
        self,
        patent,
    ):
        """
        Download one patent PDF and update the database.
        """

        print()

        print(

            f"Downloading : {patent['patent_number']}"

        )

        result = download_pdf(

            patent_number=patent["patent_number"],

            pdf_url=patent["pdf_url"],

        )

        if not result.success:

            self.repository.mark_download_failed(

                patent["id"],

                result.error,

            )

            self.failed.append(

                {

                    "patent": patent["patent_number"],

                    "stage": "download",

                    "error": result.error,

                }

            )

            return None

        self.repository.mark_downloaded(

            patent_id=patent["id"],

            local_pdf_path=str(result.pdf_path),

            file_size=result.file_size,

            download_duration=result.download_time,

        )

        self.downloaded += 1

        return result.pdf_path


    # =================================================
    # Download Pending PDFs
    # =================================================

    def download_pending_pdfs(
        self,
    ):
        """
        Download PDFs for every patent ready
        for processing.
        """

        print("=" * 60)

        print("Step 2 : Download PDFs")

        print("=" * 60)

        print()

        pending = self.pending_patents()

        if not pending:

            print(

                "No patents waiting for download."

            )

            print()

            return []

        downloaded = []

        for patent in tqdm(

            pending,

            desc="Downloading",

            unit="patent",

        ):

            pdf = self.download_patent_pdf(

                patent

            )

            if pdf is not None:

                downloaded.append(

                    (

                        patent,

                        pdf,

                    )

                )

        print()

        print(

            f"PDFs Downloaded : {len(downloaded)}"

        )

        print()

        return downloaded


    # =================================================
    # Process One Patent
    # =================================================

    def process_patent(
        self,
        patent,
        pdf_path,
    ):
        """
        Execute the complete AI pipeline for one patent.
        """

        print()

        print("=" * 60)
        print(
            f"Processing {patent['patent_number']}"
        )
        print("=" * 60)
        print()

        try:

            self.repository.mark_processing_started(
                patent["id"]
            )

            pipeline = PatentPipeline(

                pdf=pdf_path,

                classifier=self.classifier,

                detector=self.detector,

                device=self.device,

                classifier_confidence=self.classifier_confidence,

                detector_confidence=self.detector_confidence,

                padding=self.padding,

            )

            pipeline.run()

            self.processed += 1

            return True

        except Exception as error:

            print()

            print(
                f"Pipeline failed for {patent['patent_number']}"
            )

            print(error)

            print()

            self.failed.append(

                {

                    "patent": patent["patent_number"],

                    "stage": "pipeline",

                    "error": str(error),

                }

            )

            self.repository.save_failure(

                patent_number=patent["patent_number"],

                error_message=str(error),

                failure_stage="metadata",

            )

            return False


    # =================================================
    # Run AI Pipeline
    # =================================================

    def run_processing_pipeline(
        self,
    ):
        """
        Execute PatentPipeline for every downloaded PDF.
        """

        downloads = self.download_pending_pdfs()

        if not downloads:

            print()

            print("No PDFs to process.")

            return

        print()

        print("=" * 60)
        print("Step 3 : Patent Processing")
        print("=" * 60)
        print()

        total = len(downloads)

        for index, (patent, pdf_path) in enumerate(downloads, start=1):

            print()

            print("=" * 60)
            print(
                f"Patent {index} / {total}"
            )
            print(
                f"Patent Number : {patent['patent_number']}"
            )
            print("=" * 60)

            self.process_patent(
                patent,
                pdf_path,
            )

            try:
                pdf_path.unlink(
                    missing_ok=True
                )
            except Exception:
                pass

        print()

        print(
            f"Patents Processed : {self.processed}"
        )

        print()


    # =================================================
    # Summary
    # =================================================

    def print_summary(
        self,
    ):

        print()

        print("=" * 60)

        print("Pipeline Summary")

        print("=" * 60)

        print()

        print(

            f"Patent Numbers Loaded : {self.total_patents}"

        )

        print(
            f"Metadata Added        : {self.metadata_added}"
        )

        print(
            f"Metadata Skipped      : {self.metadata_skipped}"
        )

        print(

            f"PDFs Downloaded       : {self.downloaded}"

        )

        print(

            f"Patents Processed     : {self.processed}"

        )

        print(

            f"Failures              : {len(self.failed)}"

        )

        if hasattr(
            self,
            "execution_time",
        ):

            print(

                f"Execution Time        : "

                f"{self.execution_time:.2f} sec"

            )

        print()

        if self.failed:

            print("-" * 60)

            print("Failed Patents")

            print("-" * 60)

            print()

            for failure in self.failed:

                print(

                    f"{failure['patent']} "

                    f"({failure['stage']})"

                )

        print()

        print("=" * 60)


    # =================================================
    # Run
    # =================================================

    def run(
        self,
    ):

        start = time.time()

        self.fetch_and_store_metadata()

        self.run_processing_pipeline()

        self.execution_time = (

            time.time()

            - start

        )

        self.print_summary()


# =====================================================
# Main
# =====================================================

def main():

    parser = argparse.ArgumentParser(

        description=(

            "PatentStructAI "

            "Complete Patent Pipeline"

        )

    )

    parser.add_argument(

        "--patent-file",

        default=DEFAULT_PATENT_FILE,

        help=(

            "TXT file containing patent numbers."

        )

    )

    parser.add_argument(

        "--classifier",

        default="yolov8n_cls_v1",

    )

    parser.add_argument(

        "--detector",

        default="yolov8n_v2",

    )

    parser.add_argument(

        "--device",

        default="cpu",

    )

    parser.add_argument(

        "--classifier-confidence",

        type=float,

        default=0.50,

    )

    parser.add_argument(

        "--detector-confidence",

        type=float,

        default=0.25,

    )

    parser.add_argument(

        "--padding",

        type=int,

        default=10,

    )

    args = parser.parse_args()

    pipeline = PatentPipelineRunner(

        patent_file=args.patent_file,

        classifier=args.classifier,

        detector=args.detector,

        device=args.device,

        classifier_confidence=args.classifier_confidence,

        detector_confidence=args.detector_confidence,

        padding=args.padding,

    )

    pipeline.run()


if __name__ == "__main__":

    main()