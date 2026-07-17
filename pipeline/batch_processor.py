"""
PatentStructAI Batch Processor

Example
-------

Process every patent PDF inside a folder

python -m pipeline.batch_processor `
    --input data/test_pdfs

Specify classifier and detector experiments

python -m pipeline.batch_processor `
    --input data/test_pdfs `
    --classifier yolov8n_cls_v1 `
    --detector yolov8n_v2
"""

from pathlib import Path
import argparse
import json
import sys
import time
from datetime import datetime

from tqdm import tqdm

from pipeline.process_patent import PatentPipeline


# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(

    description=(

        "Batch process multiple patent PDFs."

    )

)

parser.add_argument(

    "--input",

    required=True,

    help=(

        "Directory containing patent PDFs."

    )

)

parser.add_argument(

    "--classifier",

    default="yolov8n_cls_v1",

    help=(

        "Page classifier experiment."

    )

)

parser.add_argument(

    "--detector",

    default="yolov8n_v2",

    help=(

        "Structure detector experiment."

    )

)

parser.add_argument(

    "--device",

    default="cpu",

    help=(

        "Inference device."

    )

)

parser.add_argument(

    "--classifier-confidence",

    type=float,

    default=0.50,

    help=(

        "Minimum page classification confidence."

    )

)

parser.add_argument(

    "--detector-confidence",

    type=float,

    default=0.25,

    help=(

        "Minimum detection confidence."

    )

)

parser.add_argument(

    "--padding",

    type=int,

    default=10,

    help=(

        "Crop padding."

    )

)

parser.add_argument(

    "--overwrite",

    action="store_true",

    help=(

        "Reprocess patents even if outputs already exist."

    )

)

parser.add_argument(

    "--recursive",

    action="store_true",

    help=(

        "Search for PDF files recursively."

    )

)


args = parser.parse_args()


# =====================================================
# Project Paths
# =====================================================

INPUT_DIR = Path(
    args.input
)

OUTPUT_ROOT = Path(
    "outputs"
)

BATCH_REPORTS_ROOT = (
    OUTPUT_ROOT /
    "batch_reports"
)

BATCH_REPORTS_ROOT.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# Validation
# =====================================================

def validate(input_directory):

    input_directory = Path(

        input_directory

    )

    if not input_directory.exists():

        print()

        print(

            "Input directory not found."

        )

        print(

            input_directory

        )

        sys.exit(1)

    if not input_directory.is_dir():

        print()

        print(

            "Input path is not a directory."

        )

        sys.exit(1)

# ===================================================== 
# Batch Processor 
# =====================================================

class BatchProcessor:

    def __init__(

        self,

        input_directory,

        classifier,

        detector,

        device,

        classifier_confidence,

        detector_confidence,

        padding,

        overwrite,

        recursive

    ):

        self.input_directory = Path(

            input_directory

        )

        self.classifier = classifier

        self.detector = detector

        self.device = device

        self.classifier_confidence = classifier_confidence

        self.detector_confidence = detector_confidence

        self.padding = padding

        self.overwrite = overwrite

        self.recursive = recursive

        self.successful = []

        self.skipped = []

        self.failed = []

        self.start_time = None

        self.end_time = None

        self.validate_input()

    # =================================================
    # Validate Input Directory
    # =================================================

    def validate_input(

        self

    ):

        validate(

            self.input_directory

        )

        if self.recursive:

            self.pdf_files = sorted(

                self.input_directory.rglob(

                    "*.pdf"

                )

            )

        else:

            self.pdf_files = sorted(

                self.input_directory.glob(

                    "*.pdf"

                )

            )

        if not self.pdf_files:

            print()

            print(

                "No PDF files found."

            )

            sys.exit(1)

    # =================================================
    # Print Batch Information
    # =================================================

    def print_header(self):

        print()

        print("=" * 60)

        print(

            "PatentStructAI Batch Processor"

        )

        print("=" * 60)

        print()

        print(

            f"Input Folder : {self.input_directory}"

        )

        print(

            f"Patent PDFs  : {len(self.pdf_files)}"

        )

        print(

            f"Classifier   : {self.classifier}"

        )

        print(

            f"Detector     : {self.detector}"

        )

        print()

    # =================================================
    # Process Single Patent
    # =================================================

    def process_patent(

        self,

        pdf

    ):
        
        workspace = OUTPUT_ROOT / pdf.stem

        if (

            workspace.exists()

            and

            not self.overwrite

        ):

            print(

                f"Skipping : {pdf.name}"

            )

            self.skipped.append(

                pdf.name

            )

            return

        try:

            pipeline = PatentPipeline(

                pdf=pdf,

                classifier=self.classifier,

                detector=self.detector,

                device=self.device,

                classifier_confidence=self.classifier_confidence,

                detector_confidence=self.detector_confidence,

                padding=self.padding

            )

            pipeline.run()

            self.successful.append(

                pdf.name

            )

        except Exception as error:

            print()

            print(

                f"Failed : {pdf.name}"

            )

            print(

                error

            )

            print()

            self.failed.append(

                {

                    "pdf": pdf.name,

                    "error": str(error)

                }

            )

    # =================================================
    # Run Batch Processing
    # =================================================

    def run(self):

        self.start_time = time.time()

        self.print_header()

        for pdf in tqdm(

            self.pdf_files,

            desc="Processing Patents",

            unit="patent"

        ):

            self.process_patent(

                pdf

            )

        self.end_time = time.time()

        self.report_file = self.save_report()

        self.print_summary()

    # =================================================
    # Save Batch Report
    # =================================================

    def save_report(self):

        report = {

            "timestamp":

                datetime.now().isoformat(),

            "input_directory":

                str(self.input_directory),

            "classifier":

                self.classifier,

            "detector":

                self.detector,

            "device":

                self.device,

            "total_patents":

                len(self.pdf_files),

            "successful":

                len(self.successful),

            "failed":

                len(self.failed),

            "execution_time_seconds":

                round(

                    self.end_time -

                    self.start_time,

                    2

                ),

            "average_time_per_patent":

                round(

                    (

                        self.end_time -

                        self.start_time

                    ) /

                    max(

                        len(self.pdf_files),

                        1

                    ),

                    2

            ),

            "successful_patents":

                self.successful,

            "skipped":

                len(self.skipped),

            "skipped_patents":

                self.skipped,

            "failed_patents":

                self.failed

        }

        timestamp = datetime.now().strftime(
            "%Y_%m_%d_%H%M%S"
        )

        report_file = (
            BATCH_REPORTS_ROOT /
            f"batch_report_{timestamp}.json"
        )

        with open(

            report_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                report,

                file,

                indent=4

            )

        return report_file

    # =================================================
    # Batch Summary
    # =================================================

    def print_summary(self):

        print()

        print("=" * 60)

        print(

            "Batch Processing Summary"

        )

        print("=" * 60)

        print()

        print(

            f"Total Patents      : {len(self.pdf_files)}"

        )

        print(

            f"Successful         : {len(self.successful)}"

        )

        print(

                f"Skipped           : {len(self.skipped)}"

        )

        print(

            f"Failed             : {len(self.failed)}"

        )

        print(

            f"Execution Time     : "

            f"{self.end_time - self.start_time:.2f} sec"

        )

        print(

            f"Average/Patent    : "

            f"{(self.end_time-self.start_time)/max(len(self.pdf_files),1):.2f} sec"

        )

        print()

        print(

            f"Report Saved To    :"

        )

        print(

        self.report_file

        )

        print()

        print("=" * 60)

# =====================================================
# Main
# =====================================================

def main():

    processor = BatchProcessor(

        input_directory=args.input,

        classifier=args.classifier,

        detector=args.detector,

        device=args.device,

        classifier_confidence=args.classifier_confidence,

        detector_confidence=args.detector_confidence,

        padding=args.padding,

        overwrite=args.overwrite,

        recursive=args.recursive,

    )

    processor.run()



if __name__ == "__main__":

    main()