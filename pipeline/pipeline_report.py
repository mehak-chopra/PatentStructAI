"""
PatentStructAI Pipeline Report

Example
-------

Generate a report for a single processed patent

python -m pipeline.pipeline_report \
    --patent AU2023318885A1
"""

from pathlib import Path
import argparse
import json
import sys
from datetime import datetime


# =====================================================
# Project Paths
# =====================================================

OUTPUT_ROOT = Path(
    "outputs"
)


# =====================================================
# Validation
# =====================================================

def validate_patent_workspace(
    patent
):

    workspace = (
        OUTPUT_ROOT /
        patent
    )

    if not workspace.exists():

        print()

        print(
            "Patent workspace not found."
        )

        print(
            workspace
        )

        sys.exit(1)

    metadata = (
        workspace /
        "pipeline_metadata.json"
    )

    if not metadata.exists():

        print()

        print(
            "pipeline_metadata.json not found."
        )

        print(
            metadata
        )

        sys.exit(1)

    return workspace

# =====================================================
# Pipeline Report
# =====================================================

class PipelineReport:

    def __init__(
        self,
        patent
    ):

        self.patent = patent

        self.workspace = (
            validate_patent_workspace(
                patent
            )
        )

        self.metadata_file = (
            self.workspace /
            "pipeline_metadata.json"
        )

        self.page_predictions_file = (
            self.workspace /
            "page_predictions.json"
        )

        self.structure_detections_file = (
            self.workspace /
            "structure_detections.json"
        )

        self.report_file = (
            self.workspace /
            "pipeline_report.txt"
        )

        self.report_data = self.load_metadata()

    # =================================================
    # Load Pipeline Metadata
    # =================================================

    def load_metadata(
        self
    ):

        with open(

            self.metadata_file,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(
                file
            )

    # =================================================
    # Optional JSON Loader
    # =================================================

    def load_json(
        self,
        path
    ):

        if not path.exists():

            return None

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as file:

            return json.load(
                file
            )

    # =================================================
    # Report Statistics
    # =================================================

    def collect_statistics(
        self
    ):

        pages = self.load_json(
            self.page_predictions_file
        )

        detections = self.load_json(
            self.structure_detections_file
        )

        chemistry_predictions = 0
        uncertain_predictions = 0

        if pages:

            for prediction in pages:

                label = prediction["label"]

                if label == "chemistry":

                    chemistry_predictions += 1

                elif label == "uncertain":

                    uncertain_predictions += 1

        total_detections = 0

        if detections:

            for page in detections:

                total_detections += len(

                    page["detections"]

                )

        return {

            "generated":

                datetime.now().isoformat(),

            "chemistry_predictions":

                chemistry_predictions,

            "uncertain_predictions":

                uncertain_predictions,

            "total_detections":

                total_detections

        }

    # =================================================
    # Generate Report
    # =================================================

    def generate(

        self

    ):

        stats = self.collect_statistics()

        configuration = self.report_data.get(

            "configuration",

            {}

        )

        report = [

            "=" * 60,

            "PatentStructAI Pipeline Report",

            "=" * 60,

            "",

            f"Generated : {stats['generated']}",

            "",

            "-" * 45,

            "Patent Information",

            "-" * 45,

            f"Patent : {self.report_data['patent']}",

            f"PDF    : {self.report_data['pdf']}",

            "",

            "-" * 45,

            "Pipeline Configuration",

            "-" * 45,

            f"Classifier            : {configuration.get('classifier')}",

            f"Detector              : {configuration.get('detector')}",

            f"Classifier Confidence : {configuration.get('classifier_confidence')}",

            f"Detector Confidence   : {configuration.get('detector_confidence')}",

            f"Padding               : {configuration.get('padding')}",

            f"Device                : {configuration.get('device')}",

            "",

            "-" * 45,

            "Pipeline Statistics",

            "-" * 45,

            f"Pages Extracted       : {self.report_data['total_pages']}",

            f"Chemistry Pages       : {self.report_data['chemistry_pages']}",

            f"Non-Chemistry Pages   : {self.report_data['non_chemistry_pages']}",

            f"Uncertain Pages       : {self.report_data['uncertain_pages']}",

            f"Structures Detected   : {stats['total_detections']}",

            "",

            "-" * 45,

            "Classifier Summary",

            "-" * 45,

            f"Chemistry Predictions : {stats['chemistry_predictions']}",

            f"Uncertain Predictions : {stats['uncertain_predictions']}",

            "",

            "-" * 45,

            "Workspace",

            "-" * 45,

            f"{self.workspace}",

            ""

        ]

        with open(

            self.report_file,

            "w",

            encoding="utf-8"

        ) as file:

            file.write(

                "\n".join(report)

            )

        print()

        print(

            "Pipeline report generated."

        )

        print(

            self.report_file

        )

        return self.report_file

# =====================================================
# Main
# =====================================================

def main():

    parser = argparse.ArgumentParser(

        description=(

            "Generate a human-readable report "
            "for a processed patent."

        )

    )

    parser.add_argument(

        "--patent",

        required=True,

        help=(

            "Patent number "
            "(workspace name)."

        )

    )

    args = parser.parse_args()

    report = PipelineReport(

        patent=args.patent

    )

    report.generate()


if __name__ == "__main__":

    main()