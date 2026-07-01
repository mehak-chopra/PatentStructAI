from pathlib import Path
from collections import Counter
import argparse
import sys
import yaml

# =====================================================
# Usage
#
# python -m analysis.dataset_statistics --version v2
# python -m analysis.dataset_statistics --version v3
# =====================================================


# =====================================================
# Command Line Arguments
# =====================================================

parser = argparse.ArgumentParser(
    description=(
        "Generate statistics for a versioned "
        "YOLO dataset."
    )
)

parser.add_argument(
    "--version",
    required=True,
    help="Dataset version (v1, v2, v3 ...)"
)

args = parser.parse_args()

DATASET_VERSION = args.version


# =====================================================
# Dataset Paths
# =====================================================

DATASET_ROOT = Path(
    f"annotations/datasets/{DATASET_VERSION}"
)

IMAGE_ROOT = (
    DATASET_ROOT /
    "images"
)

LABEL_ROOT = (
    DATASET_ROOT /
    "labels"
)

SPLITS = [
    "train",
    "val",
    "test"
]


# =====================================================
# Helper Functions
# =====================================================

def get_image_files(
    split
):

    return sorted(
        (
            IMAGE_ROOT /
            split
        ).glob("*.png")
    )


def get_label_files(
    split
):

    return sorted(
        (
            LABEL_ROOT /
            split
        ).glob("*.txt")
    )


def count_split_files():

    image_counts = {}

    label_counts = {}

    for split in SPLITS:

        image_counts[split] = len(
            get_image_files(split)
        )

        label_counts[split] = len(
            get_label_files(split)
        )

    return (
        image_counts,
        label_counts
    )


def total_counts(
    image_counts,
    label_counts
):

    total_images = sum(
        image_counts.values()
    )

    total_labels = sum(
        label_counts.values()
    )

    return (
        total_images,
        total_labels
    )

# =====================================================
# Annotation Statistics
# =====================================================

def get_annotation_statistics():

    class_counter = Counter()

    total_boxes = 0

    empty_labels = 0

    for split in SPLITS:

        label_files = get_label_files(
            split
        )

        for label_file in label_files:

            lines = (
                label_file
                .read_text(
                    encoding="utf-8"
                )
                .splitlines()
            )

            if not lines:

                empty_labels += 1
                continue

            for line in lines:

                parts = line.split()

                if not parts:
                    continue

                class_id = int(
                    parts[0]
                )

                class_counter[
                    class_id
                ] += 1

                total_boxes += 1

    return (
        class_counter,
        total_boxes,
        empty_labels
    )


def average_boxes_per_image(
    total_boxes,
    total_images
):

    if total_images == 0:

        return 0.0

    return (
        total_boxes /
        total_images
    )


# =====================================================
# Dataset Integrity
# =====================================================

def dataset_integrity_check():

    missing_images = []

    missing_labels = []

    for split in SPLITS:

        images = {
            image.stem
            for image in get_image_files(
                split
            )
        }

        labels = {
            label.stem
            for label in get_label_files(
                split
            )
        }

        for image in sorted(images):

            if image not in labels:

                missing_labels.append(
                    (
                        split,
                        image
                    )
                )

        for label in sorted(labels):

            if label not in images:

                missing_images.append(
                    (
                        split,
                        label
                    )
                )

    return (
        missing_images,
        missing_labels
    )

def load_class_names():

    yaml_file = (
        DATASET_ROOT /
        "data.yaml"
    )

    if not yaml_file.exists():

        return {}

    data = yaml.safe_load(
        yaml_file.read_text(
            encoding="utf-8"
        )
    )

    names = data.get(
        "names",
        {}
    )

    return {
        int(class_id): class_name
        for class_id, class_name
        in names.items()
    }

def percentage(
    value,
    total
):

    if total == 0:
        return 0.0

    return (
        value /
        total
    ) * 100

# =====================================================
# Report
# =====================================================

def print_report():

    image_counts, label_counts = (
        count_split_files()
    )

    total_images, total_labels = (
        total_counts(
            image_counts,
            label_counts
        )
    )

    (
        class_counter,
        total_boxes,
        empty_labels
    ) = get_annotation_statistics()

    (
        missing_images,
        missing_labels
    ) = dataset_integrity_check()

    average_boxes = (
        average_boxes_per_image(
            total_boxes,
            total_images
        )
    )

    print()

    print("=" * 55)
    print(
        "PatentStructAI Dataset Statistics"
    )

    print("=" * 55)

    print()

    print(
        f"Ultralytics YOLO Detection Dataset"
    )

    print()

    print(
        f"Dataset Version   : {DATASET_VERSION}"
    )

    print()

    print("-" * 40)
    print("Images")
    print("-" * 40)

    print(
        f"Training Images   : "
        f"{image_counts['train']} "
        f"({percentage(image_counts['train'], total_images):.1f}%)"
    )

    print(
        f"Validation Images : "
        f"{image_counts['val']} "
        f"({percentage(image_counts['val'], total_images):.1f}%)"
    )

    print(
        f"Testing Images    : "
        f"{image_counts['test']} "
        f"({percentage(image_counts['test'], total_images):.1f}%)"
    )

    print()

    print(
        f"Total Images      : "
        f"{total_images}"
    )

    dataset_size = sum(
        image.stat().st_size
        for split in SPLITS
        for image in get_image_files(split)
    )

    print(
        f"Dataset Size      : "
        f"{dataset_size / (1024 * 1024):.2f} MB"
    )

    print()

    print("-" * 40)
    print("Labels")
    print("-" * 40)

    print(
        f"Training Labels   : "
        f"{label_counts['train']}"
    )

    print(
        f"Validation Labels : "
        f"{label_counts['val']}"
    )

    print(
        f"Testing Labels    : "
        f"{label_counts['test']}"
    )

    print()

    print(
        f"Total Labels      : "
        f"{total_labels}"
    )

    print()

    print("-" * 40)
    print("Annotation Statistics")
    print("-" * 40)

    if class_counter:

        class_names = load_class_names()

        for class_id in sorted(
            class_counter
        ):

            LABEL_WIDTH = 21

            print(
                f"{class_names.get(class_id, f'Class {class_id}'):<{LABEL_WIDTH}}"
                f": {class_counter[class_id]}"
            )

    else:

        print(
            "No annotations found."
        )

    print()

    print(
        f"Total Bounding Boxes : "
        f"{total_boxes}"
    )

    print(
        f"Average Boxes/Image  : "
        f"{average_boxes:.2f}"
    )

    print(
        f"Empty Label Files    : "
        f"{empty_labels}"
    )

    print()

    print("-" * 40)
    print("Dataset Integrity")
    print("-" * 40)

    print(
        f"Missing Images : "
        f"{len(missing_images)}"
    )

    print(
        f"Missing Labels : "
        f"{len(missing_labels)}"
    )

    if (
        not missing_images
        and
        not missing_labels
        and
        empty_labels == 0
    ):

        print()
        print(
            "✓ Dataset Integrity Check Passed"
        )

    else:

        print()

        print(
            "✗ Dataset Integrity Check Failed"
        )

        if missing_images:

            print()

            print(
                "Images missing for labels:"
            )

            for split, name in missing_images:

                print(
                    f"  [{split}] {name}.txt"
                )

        if missing_labels:

            print()

            print(
                "Labels missing for images:"
            )

            for split, name in missing_labels:

                print(
                    f"  [{split}] {name}.png"
                )

        sys.exit(1)

    print()

    print("-" * 40)
    print("Dataset Location")
    print("-" * 40)

    print(
        DATASET_ROOT.as_posix()
    )

    print()


# =====================================================
# Main
# =====================================================

def main():

    if not DATASET_ROOT.exists():

        print(
            f"Dataset not found: "
            f"{DATASET_ROOT}"
        )

        sys.exit(1)

    print_report()


if __name__ == "__main__":

    main()
