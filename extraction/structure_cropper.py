"""
PatentStructAI Structure Cropper

Example
-------

Crop structures from extracted patent pages

python -m extraction.structure_cropper \
    --experiment yolov8n_v2

python -m extraction.structure_cropper \
    --experiment yolov8n_v2 \
    --conf 0.40 \
    --padding 15

python -m extraction.structure_cropper \
    --experiment yolov8n_v2 \
    --overwrite
"""

from pathlib import Path
import argparse
import json
import sys

import cv2

from ultralytics import YOLO

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(".")

EXPERIMENTS_ROOT = (
    PROJECT_ROOT /
    "models" /
    "structure_detector" /
    "experiments"
)

EXTRACTED_IMAGES_ROOT = (
    PROJECT_ROOT /
    "data" /
    "extracted_images"
)

CROPPED_STRUCTURES_ROOT = (
    PROJECT_ROOT /
    "data" /
    "cropped_structures"
)

# =====================================================
# Experiment Paths
# =====================================================

def experiment_paths(experiment):

    detector = (
        EXPERIMENTS_ROOT /
        experiment
    )

    return {

        "experiment":
            detector,

        "weights":
            detector /
            "weights" /
            "best.pt"

    }

# =====================================================
# Validation
# =====================================================

def validate(experiment):

    paths = experiment_paths(
        experiment
    )

    if not paths["experiment"].exists():

        print(
            "Experiment not found."
        )

        sys.exit(1)

    if not paths["weights"].exists():

        print(
            "best.pt not found."
        )

        sys.exit(1)

    if not EXTRACTED_IMAGES_ROOT.exists():

        print(
            "Extracted images folder not found."
        )

        sys.exit(1)

    CROPPED_STRUCTURES_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

# =====================================================
# Structure Cropper
# =====================================================

class StructureCropper:

    def __init__(
        self,
        experiment,
        conf=0.25,
        padding=10,
        device=None,
        overwrite=False
    ):

        self.experiment = experiment
        self.conf = conf
        self.padding = padding
        self.device = device
        self.overwrite = overwrite
        self.paths = experiment_paths(
            experiment
        )
        self.extracted_images_root = EXTRACTED_IMAGES_ROOT

        self.output_root = CROPPED_STRUCTURES_ROOT

        self.detector = self.load_detector()

    # =================================================
    # Load Detector
    # =================================================

    def load_detector(self):

        print()

        print("=" * 55)
        print("Loading Chemical Structure Detector")
        print("=" * 55)
        print()

        print(
            f"Experiment : {self.experiment}"
        )

        print(
            f"Weights    : {self.paths['weights']}"
        )

        print()

        model = YOLO(
            self.paths["weights"]
        )

        print(
            "Detector loaded successfully."
        )

        return model

    # =================================================
    # Discover Patent Folders
    # =================================================

    def discover_patents(self):

        patents = []

        for folder in sorted(
            self.extracted_images_root.iterdir()
        ):

            if folder.is_dir():

                patents.append(
                    folder
                )

        return patents

    # =================================================
    # Prepare Patent Workspace
    # =================================================

    def prepare_patent_workspace(
        self,
        patent_folder
    ):

        output = (

            self.output_root /

            patent_folder.name

        )

        output.mkdir(

            parents=True,

            exist_ok=True

        )

        return output

    # =================================================
    # Load Page
    # =================================================

    def load_page(
        self,
        image_path
    ):

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            raise RuntimeError(

                f"Unable to load\n"

                f"{image_path}"

            )

        return image

    # =================================================
    # Detect Structures
    # =================================================

    def detect_structures(
        self,
        image
    ):

        prediction = self.detector(

            image,

            conf=self.conf,

            device=self.device,

            verbose=False

        )

        return prediction[0]

    # =================================================
    # Crop Detection
    # =================================================

    def crop_detection(
        self,
        image,
        box
    ):

        height, width = image.shape[:2]

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        x1 = max(
            0,
            x1 - self.padding
        )

        y1 = max(
            0,
            y1 - self.padding
        )

        x2 = min(
            width,
            x2 + self.padding
        )

        y2 = min(
            height,
            y2 + self.padding
        )

        crop = image[
            y1:y2,
            x1:x2
        ]

        return crop, [

            x1,
            y1,
            x2,
            y2

        ]

    # =================================================
    # Save Crop
    # =================================================

    def save_crop(
        self,
        crop,
        page_folder,
        index
    ):

        filename = (

            f"structure_{index:03d}.png"

        )

        output = (

            page_folder /

            filename

        )

        cv2.imwrite(

            str(output),

            crop

        )

        return output
    
    # =================================================
    # Process Single Page
    # =================================================

    def process_page(
        self,
        image_path,
        output_folder
    ):

        image = self.load_page(
            image_path
        )

        detections = self.detect_structures(
            image
        )

        page_folder = (

            output_folder /

            image_path.stem

        )

        page_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        metadata = []

        count = 0

        for box in detections.boxes:

            confidence = float(
                box.conf[0]
            )

            crop, bbox = self.crop_detection(
                image,
                box
            )

            count += 1

            crop_path = self.save_crop(
                crop,
                page_folder,
                count
            )

            metadata.append({

                "file":
                    crop_path.relative_to(
                        output_folder
                    ).as_posix(),

                "confidence":
                    round(
                        confidence,
                        4
                    ),

                "bbox":
                    bbox,

                "width":
                    crop.shape[1],

                "height":
                    crop.shape[0]

            })

        return metadata
    
    # =================================================
    # Process Multiple Pages
    # =================================================

    def process_pages(

        self,

        pages,

        output_folder

    ):

        total_structures = 0

        page_metadata = []

        output_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        for page in pages:

            detections = self.process_page(

                page,

                output_folder

            )

            total_structures += len(

                detections

            )

            page_metadata.append({

                "page":

                    page.name,

                "detections":

                    detections

            })

        return {

            "structures": total_structures,

            "metadata": page_metadata

        }

    # =================================================
    # Process Patent
    # =================================================

    def process_patent(
        self,
        patent_folder
    ):

        print()

        print(
            f"Processing {patent_folder.name}"
        )

        output = self.prepare_patent_workspace(
            patent_folder
        )

        pages = sorted(
            patent_folder.glob("*.png")
        )

        patent_metadata = {

            "patent":
                patent_folder.name,

            "pages_processed":
                0,

            "structures_found":
                0,

            "structures":
                []

        }

        for page in pages:

            page_data = self.process_page(
                page,
                output
            )

            patent_metadata[
                "pages_processed"
            ] += 1

            patent_metadata[
                "structures_found"
            ] += len(
                page_data
            )

            patent_metadata[
                "structures"
            ].append({

                "page":
                    page.stem,

                "detections":
                    page_data

            })

        return output, patent_metadata

    # =================================================
    # Save Metadata
    # =================================================

    def save_metadata(
        self,
        output_folder,
        metadata
    ):

        metadata_file = (

            output_folder /

            "metadata.json"

        )

        with open(

            metadata_file,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                metadata,

                file,

                indent=4

            )

        return metadata_file
    
    # =================================================
    # Process Entire Dataset
    # =================================================

    def process_dataset(self):

        total_patents = 0

        total_pages = 0

        total_structures = 0

        patents = self.discover_patents()

        print()

        print(

            f"Patents discovered : {len(patents)}"

        )

        for patent in patents:

            workspace = (

                self.output_root /

                patent.name

            )

            if (

                workspace.exists()

                and

                not self.overwrite

            ):

                print(

                    f"Skipping {patent.name}"

                )

                continue

            output = self.prepare_patent_workspace(

                patent

            )

            output, metadata = (

                self.process_patent(

                    patent

                )

            )

            self.save_metadata(

                output,

                metadata

            )

            total_patents += 1

            total_pages += metadata[

                "pages_processed"

            ]

            total_structures += metadata[

                "structures_found"

            ]

        print()

        print(
            "Cropping completed successfully."
        )

        return {

            "patents": total_patents,

            "pages": total_pages,

            "structures": total_structures

        }

# =====================================================
# Crop Summary
# =====================================================

def print_summary(

    stats,

    output_folder

):

    print()

    print("=" * 60)

    print(
        "PatentStructAI Crop Summary"
    )

    print("=" * 60)

    print()

    print(

        f"Patents Processed : {stats['patents']}"

    )

    print(

        f"Pages Processed   : {stats['pages']}"

    )

    print(

        f"Structures Found  : {stats['structures']}"

    )

    if stats["pages"]:

        print(

            f"Average Structures/Page : "

            f"{stats['structures']/stats['pages']:.2f}"

        )

    print()

    print(
        "Output Folder :"
    )

    print(
        output_folder
    )

    print()

    print("=" * 60)

# =====================================================
# Save Crop Report
# =====================================================

def save_crop_report(
    stats,
    output_folder,
    experiment,
    confidence,
    padding
):

    report = [

        "=" * 60,

        "PatentStructAI Crop Report",

        "=" * 60,

        "",

        f"Patents Processed : {stats['patents']}",

        f"Pages Processed   : {stats['pages']}",

        f"Structures Found  : {stats['structures']}",

        "",

        f"Average Structures/Page : "

        f"{stats['structures']/max(stats['pages'],1):.2f}",

        "",

        f"Detector : {experiment}",

        f"Confidence : {confidence}",

        f"Padding : {padding}",

        "",

        f"Output Folder : {output_folder}"

    ]

    with open(

        output_folder /

        "crop_report.txt",

        "w",

        encoding="utf-8"

    ) as file:

        file.write(

            "\n".join(report)

        )

# =====================================================
# Main
# =====================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Crop detected chemical structures "
            "from patent page images."
        )
    )

    parser.add_argument(
        "--experiment",
        required=True,
        help=(
            "Detector experiment "
            "(example: yolov8n_v2)"
        )
    )

    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help=(
            "Minimum confidence "
            "required to keep a detection."
        )
    )

    parser.add_argument(
        "--padding",
        type=int,
        default=10,
        help=(
            "Pixels of padding "
            "added around each crop."
        )
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Overwrite already processed patents."
        )
    )

    parser.add_argument(
        "--device",
        default=None,
        help=(
            "Inference device "
            "(cpu, cuda, cuda:0...)"
        )
    )

    args = parser.parse_args()

    validate(args.experiment)

    cropper = StructureCropper(

        experiment=args.experiment,

        conf=args.conf,

        padding=args.padding,

        device=args.device,

        overwrite=args.overwrite

    )

    stats = cropper.process_dataset()

    save_crop_report(

        stats,

        cropper.output_root,

        args.experiment,

        args.conf,

        args.padding

    )

    print_summary(

        stats,

        cropper.output_root

    )


if __name__ == "__main__":

    main()