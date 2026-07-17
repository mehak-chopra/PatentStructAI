"""
PatentStructAI Patent Processing Pipeline

Example
-------

Process one patent

python -m pipeline.process_patent `
    --pdf data/temp/US1234567.pdf

Specify classifier and detector experiments

python -m pipeline.process_patent `
    --pdf data/test_pdfs/AU2023318885A1.pdf `
    --classifier yolov8n_cls_v1 `
    --detector yolov8n_v2
"""

from pathlib import Path
import argparse
import json
import shutil
import sys
from datetime import datetime
import time
import importlib

# Existing PatentStructAI modules
from extraction.image_extractor import (
    render_pdf_pages
)

from extraction.page_classifier import PageClassifier
from extraction.structure_cropper import StructureCropper

from chemistry.smiles_extractor import SMILESExtractor
from chemistry.recognizers.molnextr_recognizer import MolNexTRRecognizer

from database.patent_repository import PatentRepository
from database.patent_page_repository import PatentPageRepository
from database.structure_repository import StructureRepository

from database.models import (
    PatentPageRecord,
    StructureRecordDB,
)

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(".")

MODELS_ROOT = (
    PROJECT_ROOT /
    "models"
)

OUTPUT_ROOT = (
    PROJECT_ROOT /
    "outputs"
)

# =====================================================
# Validation
# =====================================================

def validate(pdf):

    pdf = Path(
        pdf
    )

    if not pdf.exists():
        print()

        print(
            "Patent PDF not found."
        )

        print(
            pdf
        )

        sys.exit(1)

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

# =====================================================
# Patent Processing Pipeline
# =====================================================

class PatentPipeline:

    def __init__(
        self,
        pdf,
        classifier,
        detector,
        device,
        classifier_confidence,
        detector_confidence,
        padding
    ):

        self.pdf = Path(
            pdf
        )

        self.patent = self.pdf.stem

        self.device = device

        self.classifier_name = classifier

        self.detector_name = detector

        self.classifier_confidence = classifier_confidence

        self.detector_confidence = detector_confidence

        self.padding = padding

        # -------------------------------------------------
        # Chemistry Pipeline
        # -------------------------------------------------

        self.recognizer = MolNexTRRecognizer()

        self.smiles_extractor = SMILESExtractor(
            recognizer=self.recognizer
        )

        # -------------------------------------------------
        # Database Repositories
        # -------------------------------------------------

        self.patent_repository = PatentRepository()

        self.page_repository = PatentPageRepository()

        self.structure_repository = StructureRepository()

        self.patent_id = None

        self.workspace = (
            OUTPUT_ROOT /
            self.patent
        )

        self.pages_dir = (
            self.workspace /
            "pages"
        )

        self.chemistry_pages_dir = (
            self.workspace /
            "chemistry_pages"
        )

        self.crops_dir = (
            self.workspace /
            "structures"
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

        self.chemistry_results_file = (
            self.workspace /
            "chemistry_results.json"
        )

        self.chemistry_results = []

        self.searchable_structures = []

        self.prepare_workspace()

    # =================================================
    # Environment Check
    # =================================================

    def check_environment(self):

        print("=" * 60)
        print("Environment Check")
        print("=" * 60)
        print()

        modules = {
            "torch": "PyTorch",
            "cv2": "OpenCV",
            "rdkit": "RDKit",
            "MolNexTR": "MolNexTR",
        }

        for module, name in modules.items():
            try:
                importlib.import_module(module)
                print(f"[OK] {name}")

            except Exception as error:

                raise RuntimeError(
                    f"{name} could not be imported.\n{error}"
                )

        classifier_weights = (
            MODELS_ROOT
            / "page_classifier"
            / "experiments"
            / self.classifier_name
            / "weights"
            / "best.pt"
        )

        if not classifier_weights.exists():
            raise FileNotFoundError(
                f"Classifier weights not found:\n{classifier_weights}"
            )

        print("[OK] Page Classifier Weights")

        detector_weights = (
            MODELS_ROOT
            / "structure_detector"
            / "experiments"
            / self.detector_name
            / "weights"
            / "best.pt"
        )

        if not detector_weights.exists():
            raise FileNotFoundError(
                f"Detector weights not found:\n{detector_weights}"
            )

        print("[OK] Structure Detector Weights")

        print()

    # =================================================
    # Prepare Workspace
    # =================================================

    def prepare_workspace(self):

        self.workspace.mkdir(
            parents=True,
            exist_ok=True
        )

        self.pages_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.chemistry_pages_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.crops_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print()

        print("=" * 60)

        print(
            "PatentStructAI Processing Pipeline"
        )

        print("=" * 60)

        print()

        print(
            f"Patent        : {self.patent}"
        )

        print(
            f"Classifier    : {self.classifier_name}"
        )

        print(
            f"Detector      : {self.detector_name}"
        )

        print(
            f"Workspace     : {self.workspace}"
        )

        print()

    # =================================================
    # Save Patent
    # =================================================

    def save_patent(self):
        """
        Ensure the patent exists in the database and cache
        its database ID.
        """

        from database.models import PatentRecord

        patent = PatentRecord(
            patent_number=self.patent,
            title=None,
            pdf_url=None,
            country=None,
        )

        self.patent_repository.save(
            patent
        )

        record = self.patent_repository.get_by_number(
            self.patent
        )

        self.patent_id = record["id"]

    # =================================================
    # Extract Patent Pages
    # =================================================

    def extract_pages(self):

        print()

        print("=" * 60)

        print("Step 1 : Extract Patent Pages")

        print("=" * 60)

        print()

        page_records = render_pdf_pages(
            pdf_path=self.pdf,
            patent_number=self.patent,
            output_dir=self.pages_dir
        )

        self.page_images = [
            Path(
                record["image_path"]
            )
            for record in page_records
        ]

        self.total_pages = len(
            self.page_images
        )

        for page_number, image_path in enumerate(
            self.page_images,
            start=1,
        ):

            page = PatentPageRecord(
                patent_id=self.patent_id,
                page_number=page_number,
                image_path=str(image_path),
            )

            self.page_repository.save(page)

        print(
            f"Pages Extracted : {self.total_pages}"
        )

        print()

        return self.page_images

    # =================================================
    # Load Page Classifier
    # =================================================

    def load_classifier(self):

        print("=" * 60)

        print(
            "Step 2 : Load Page Classifier"
        )

        print("=" * 60)

        print()

        weights = (
            MODELS_ROOT /
            "page_classifier" /
            "experiments" /
            self.classifier_name /
            "weights" /
            "best.pt"
        )

        self.classifier = PageClassifier(
            weights=weights,
            device=self.device,
            confidence=self.classifier_confidence
        )

        print(
            "Page classifier loaded."
        )

        print()

    # =================================================
    # Classify Pages
    # =================================================

    def classify_pages(self):

        print("=" * 60)

        print(
            "Step 3 : Page Classification"
        )

        print("=" * 60)

        print()

        self.chemistry_pages = []
        self.non_chemistry_pages = []
        self.uncertain_pages = []
        self.total_structures = 0
        self.structure_metadata = []

        predictions = self.classifier.predict_batch(
            self.page_images
        )

        self.page_predictions = predictions

        pages = self.page_repository.get_by_patent(
            self.patent_id
        )

        for prediction in predictions:
            image = Path(
                prediction["image"]
            )

            page_number = int(
                image.stem.split("_")[-1]
            )

            label = prediction["label"]

            confidence = prediction["confidence"]

            print(
                f"{image.name:<25}"
                f"{label:<18}"
                f"{confidence:.4f}"
            )

            page = pages[page_number - 1]

            contains = None

            if label == "chemistry":
                contains = True

            elif label == "non_chemistry":
                contains = False

            self.page_repository.update_classification(
                page_id=page["id"],
                contains_chemistry=contains,
                chemistry_score=confidence,
            )

            if label == "chemistry":
                self.chemistry_pages.append(
                    image
                )

            elif label == "non_chemistry":
                self.non_chemistry_pages.append(
                    image
                )

            else:
                self.uncertain_pages.append(
                    image
                )

        print()

        print("-" * 60)

        print(
            f"Chemistry Pages     : {len(self.chemistry_pages)}"
        )

        print(
            f"Non-Chemistry Pages : {len(self.non_chemistry_pages)}"
        )

        print(
            f"Uncertain Pages     : {len(self.uncertain_pages)}"
        )

        print()

    # =================================================
    # Save Page Predictions
    # =================================================

    def save_page_predictions(self):

        with open(
            self.page_predictions_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(

                self.page_predictions,
                file,
                indent=4
            )

    # =================================================
    # Copy Chemistry Pages
    # =================================================

    def prepare_chemistry_pages(self):

        print("=" * 60)

        print(
            "Preparing Chemistry Pages"
        )

        print("=" * 60)

        print()

        for page in self.chemistry_pages:
            destination = (
                self.chemistry_pages_dir /
                page.name
            )

            shutil.copy2(
                page,
                destination
            )

        print(
            f"Copied {len(self.chemistry_pages)} pages."
        )

        print()

    # =================================================
    # Load Structure Detector
    # =================================================

    def load_detector(self):

        print("=" * 60)

        print(
            "Step 4 : Load Structure Detector"
        )

        print("=" * 60)

        print()

        self.cropper = StructureCropper(
            experiment=self.detector_name,
            conf=self.detector_confidence,
            padding=self.padding,
            device=self.device
        )

        print(
            "Structure detector loaded."
        )

        print()

    # =================================================
    # Detect Structures
    # =================================================

    def detect_structures(self):

        print("=" * 60)

        print(
            "Step 5 : Detect Structures"
        )

        print("=" * 60)

        print()

        self.total_structures = 0
        self.structure_metadata = []

        for page in self.chemistry_pages:

            print(
                f"Processing {page.name}"
            )

            detections = self.cropper.process_page(
                page,
                self.crops_dir
            )

            self.total_structures += len(
                detections
            )

            self.structure_metadata.append({
                "page":
                    page.name,
                "detections":
                    detections
            })

        print()

        print(
            f"Structures Detected : {self.total_structures}"
        )

        print()

    # =================================================
    # Extract Chemistry
    # =================================================

    def extract_chemistry(self):

        print("=" * 60)

        print(
            "Step 6 : Molecular Recognition"
        )

        print("=" * 60)

        print()

        self.chemistry_results = []
        self.searchable_structures = []

        structure_index = 1

        for crop in sorted(
            self.crops_dir.rglob("*.png")
        ):
            
            page_number = int(
                crop.parent.name.split("_")[-1]
            )

            print(
                f"Recognizing {crop.name}"
            )

            result = self.smiles_extractor.extract_from_path(
                image_path=crop,
                patent_id=self.patent,
                page_number=page_number,
                structure_id=f"STR{structure_index:06d}",
            )

            self.chemistry_results.append(result)

            if result.searchable:

                self.searchable_structures.append(
                    result.structure
                )
            
                structure = StructureRecordDB(
                    patent_id=self.patent_id,
                    page_number=page_number,
                    crop_index=structure_index,
                    image_path=str(crop),

                    smiles=(
                        result.structure.smiles
                        if result.structure
                        else None
                    ),

                    canonical_smiles=(
                        result.structure.canonical_smiles
                        if result.structure
                        else None
                    ),

                    molblock=(
                        result.recognition.molblock
                        if result.recognition
                        else None
                    ),

                    fingerprint_hash=(
                        result.structure.fingerprint_hash
                        if result.structure
                        else None
                    ),

                    recognizer_name=(
                        result.recognition.recognizer
                        if result.recognition
                        else None
                    ),

                    recognizer_version=(
                        result.recognition.recognizer_version
                        if result.recognition
                        else None
                    ),

                    recognizer_confidence=(
                        result.structure.recognition_confidence
                        if result.structure
                        else None
                    ),

                    backend=(
                        result.recognition.device
                        if result.recognition
                        else None
                    ),

                    inference_time=(
                        result.structure.inference_time
                        if result.structure
                        else None
                    ),

                    pipeline_time=result.elapsed_time,

                    recognition_success=(
                        result.recognition.success
                        if result.recognition
                        else False
                    ),

                    failure_reason=(
                        result.error
                        if result.error
                        else (
                            result.recognition.error
                            if result.recognition
                            else None
                        )
                    ),

                    searchable=result.searchable,
                )

                self.structure_repository.save(structure)

            structure_index += 1

        print()

        print(
            f"Structures Processed : {len(self.chemistry_results)}"
        )

        print(
            f"Searchable Structures : {len(self.searchable_structures)}"
        )

        print()

    # =================================================
    # Save Chemistry Results
    # =================================================

    def save_chemistry_results(self):

        data = []

        for result in self.chemistry_results:

            item = result.summary()

            if result.structure is not None:

                item["structure"] = {
                    "structure_id": result.structure.structure_id,
                    "patent_id": result.structure.patent_id,
                    "page_number": result.structure.page_number,
                    "image_path": (
                        str(result.structure.image_path)
                        if result.structure.image_path
                        else None
                    ),
                    "canonical_smiles": (
                        result.structure.canonical_smiles
                    ),
                    "fingerprint_hash": (
                        result.structure.fingerprint_hash
                    ),
                }

            data.append(item)

        with open(
            self.chemistry_results_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
            )

        print(
            f"Chemistry results saved to {self.chemistry_results_file}"
        )

        print()

    # =================================================
    # Save Structure Detections
    # =================================================

    def save_structure_detections(self):

        with open(
            self.structure_detections_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.structure_metadata,
                file,
                indent=4
            )

    # =================================================
    # Save Pipeline Metadata
    # =================================================

    def save_metadata(self):

        metadata = {

            "patent":
                self.patent,

            "timestamp":
                datetime.now().isoformat(),

            "pdf":
                str(self.pdf),

            "configuration": {
                "classifier":
                    self.classifier_name,

                "detector":
                    self.detector_name,

                "classifier_confidence":
                    self.classifier_confidence,

                "detector_confidence":
                    self.detector_confidence,

                "padding":
                    self.padding,

                "device":
                    self.device

            },

            "total_pages":
                self.total_pages,

            "chemistry_pages":
                len(self.chemistry_pages),

            "non_chemistry_pages":
                len(self.non_chemistry_pages),

            "uncertain_pages":
                len(self.uncertain_pages),

            "structures":
                self.total_structures,

            "structure_detections":
                self.structure_metadata
        }

        with open(
            self.metadata_file,
            "w",
            encoding="utf-8"

        ) as file:
            json.dump(
                metadata,
                file,
                indent=4
            )

    # =================================================
    # Pipeline Summary
    # =================================================

    def print_summary(self):

        print()

        print("=" * 60)

        print("Pipeline Summary")

        print("=" * 60)

        print()

        print(f"Patent               : {self.patent}")

        print(f"Pages Extracted      : {self.total_pages}")

        print(f"Chemistry Pages      : {len(self.chemistry_pages)}")

        print(f"Structures Detected  : {self.total_structures}")

        print(f"Searchable Structures : {len(self.searchable_structures)}")

        if hasattr(self, "execution_time"):

            print(

                f"Execution Time       : {self.execution_time:.2f} sec"

            )

        print()

        print(f"Workspace            : {self.workspace}")

        print()

        print("=" * 60)

    # =================================================
    # Run Pipeline
    # =================================================

    def run(self):

        try:

            start = time.time()

            self.check_environment()

            self.save_patent()

            self.extract_pages()

            self.patent_repository.mark_images_extracted(
                self.patent_id
            )

            self.load_classifier()

            self.classify_pages()

            self.prepare_chemistry_pages()

            if not self.chemistry_pages:

                print(

                    "No chemistry pages detected."

                )

                self.save_page_predictions()

                self.save_metadata()

                self.print_summary()

                return

            self.load_detector()

            self.detect_structures()

            self.extract_chemistry()

            self.patent_repository.mark_structures_extracted(
                self.patent_id
            )

            self.save_chemistry_results()

            self.save_page_predictions()

            self.save_structure_detections()

            self.save_metadata()

            self.patent_repository.mark_processed(
                self.patent_id
            )

            print(
                "Pipeline artifacts saved."
            )

            print()

            elapsed = time.time() - start

            self.execution_time = elapsed

            print(
                f"Execution Time : {self.execution_time:.2f} sec"
            )

            self.print_summary()

        except Exception as error:

            print()

            print(
                "Pipeline failed."
            )

            print(
                error
            )

            raise

# =====================================================
# Main
# =====================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "Complete PatentStructAI "
            "processing pipeline."
        )

    )

    parser.add_argument(
        "--pdf",
        required=True,

        help=(
            "Patent PDF to process."
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

    args = parser.parse_args()

    validate(
        args.pdf
    )

    pipeline = PatentPipeline(
        pdf=args.pdf,
        classifier=args.classifier,
        detector=args.detector,
        device=args.device,
        classifier_confidence=args.classifier_confidence,
        detector_confidence=args.detector_confidence,
        padding=args.padding
    )

    pipeline.run()


if __name__ == "__main__":
    main()