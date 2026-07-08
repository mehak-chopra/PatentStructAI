"""
PatentStructAI Dataset Statistics

Generate comprehensive statistics for a versioned
YOLO object detection dataset.

Features
--------
- Image and label counts
- Train / Validation / Test split statistics
- Dataset size
- Bounding box statistics
- Class distribution
- Most / Least annotated pages
- Dataset integrity verification

Example
-------

python -m analysis.dataset_statistics \
    --version v1

python -m analysis.dataset_statistics \
    --version v2
"""

from pathlib import Path
from collections import Counter
import argparse
import sys
import yaml

# =====================================================
# Dataset Paths
# =====================================================

SPLITS = [
    "train",
    "val",
    "test"
]

# =====================================================
# Dataset Paths
# =====================================================

def dataset_paths(version):
    dataset_root = (
        Path("annotations")
        / "datasets"
        / version
    )

    return {
        "root":
            dataset_root,

        "images":
            dataset_root /
            "images",

        "labels":
            dataset_root /
            "labels",

        "yaml":
            dataset_root /
            "data.yaml"
    }

# =====================================================
# Helper Functions
# =====================================================

def get_image_files(
    image_root,
    split
):

    return sorted(
        (
            image_root /
            split
        ).glob(
            "*.png"
        )
    )


def get_label_files(
    label_root,
    split
):

    return sorted(
        (
            label_root /
            split
        ).glob("*.txt")
    )


def count_split_files(
    image_root,
    label_root
):

    image_counts = {}
    label_counts = {}
    image_files = {}
    label_files = {}

    for split in SPLITS:

        images = get_image_files(
            image_root,
            split
        )

        labels = get_label_files(
            label_root,
            split
        )

        image_files[split] = images

        label_files[split] = labels

        image_counts[split] = len(
            images
        )

        label_counts[split] = len(
            labels
        )

    return (
        image_counts,
        label_counts,
        image_files,
        label_files
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

def get_annotation_statistics(
    label_files
):

    class_counter = Counter()
    total_boxes = 0
    empty_labels = 0
    annotation_counts = []

    most_annotations = {
        "page": None,
        "count": 0
    }

    least_annotations = {
        "page": None,
        "count": float("inf")
    }

    for split in SPLITS:
        for label_file in label_files[split]:

            lines = (
                label_file
                .read_text(
                    encoding="utf-8"
                )
                .splitlines()
            )

            annotation_count = len(lines)

            annotation_counts.append(
                annotation_count
            )

            if annotation_count == 0:
                empty_labels += 1

            if annotation_count > most_annotations["count"]:
                most_annotations = {
                    "page": label_file.name,
                    "count": annotation_count
                }

            if annotation_count < least_annotations["count"]:
                least_annotations = {
                    "page": label_file.name,
                    "count": annotation_count
                }

            for line in lines:
                parts = line.split()
                if not parts:
                    continue

                class_counter[
                    int(parts[0])
                ] += 1

                total_boxes += 1

    if least_annotations["count"] == float("inf"):
        least_annotations["count"] = 0

    return (
        class_counter,
        total_boxes,
        empty_labels,
        annotation_counts,
        most_annotations,
        least_annotations
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


def dataset_size_mb(
    image_files
):

    total = 0

    for split in SPLITS:
        for image in image_files[split]:
            total += image.stat().st_size
    return total / (1024 * 1024)


def median_annotations(
    annotation_counts
):

    if not annotation_counts:
        return 0

    annotation_counts = sorted(
        annotation_counts
    )

    n = len(annotation_counts)

    middle = n // 2

    if n % 2 == 0:
        return (
            annotation_counts[middle - 1] +
            annotation_counts[middle]
        ) / 2

    return annotation_counts[middle]


def max_annotations(
    annotation_counts
):

    if not annotation_counts:
        return 0

    return max(
        annotation_counts
    )


def min_annotations(
    annotation_counts
):

    if not annotation_counts:
        return 0

    return min(
        annotation_counts
    )


# =====================================================
# Dataset Integrity
# =====================================================

def dataset_integrity_check(
    image_files,
    label_files
):

    missing_images = []
    missing_labels = []

    for split in SPLITS:

        images = {
            image.stem
            for image in image_files[split]
        }

        labels = {
            label.stem
            for label in label_files[split]
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


def load_class_names(
    yaml_file
):

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
        for class_id,
        class_name
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

def print_report(
    dataset_version
):

    paths = dataset_paths(
        dataset_version
    )

    image_counts, label_counts, image_files, label_files = (

        count_split_files(
            paths["images"],
            paths["labels"]
        )
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
        empty_labels,
        annotation_counts,
        most_annotations,
        least_annotations
    ) = get_annotation_statistics(
        label_files
    )

    (
        missing_images,
        missing_labels
    ) = dataset_integrity_check(
        image_files,
        label_files
    )

    average_boxes = average_boxes_per_image(
        total_boxes,
        total_images
    )

    dataset_size = dataset_size_mb(
        image_files
    )

    class_names = load_class_names(
        paths["yaml"]
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
        f"Dataset Version   : {dataset_version}"
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

    print(
        f"Dataset Size      : "
        f"{dataset_size:.2f} MB"
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
    print("Chemical Structure Annotation Statistics")
    print("-" * 40)

    if class_counter:

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
        f"Median Boxes/Image   : "
        f"{median_annotations(annotation_counts):.2f}"
    )

    print(
        f"Maximum Boxes/Image  : "
        f"{max_annotations(annotation_counts)}"
    )

    print(
        f"Minimum Boxes/Image  : "
        f"{min_annotations(annotation_counts)}"
    )

    print(
        f"Most Annotated Page  : "
        f"{most_annotations['page']}"
    )

    print(
        f"Boxes On That Page   : "
        f"{most_annotations['count']}"
    )

    print(
        f"Least Annotated Page : "
        f"{least_annotations['page']}"
    )

    print(
        f"Boxes On That Page   : "
        f"{least_annotations['count']}"
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
        paths["root"].as_posix()
    )

    print()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate statistics for a "
            "versioned YOLO dataset."
        )
    )

    parser.add_argument(
        "--version",
        required=True,
        help=(
            "Dataset version "
            "(v1, v2, v3...)"
        )
    )

    args = parser.parse_args()
    paths = dataset_paths(
        args.version
    )

    if not paths["root"].exists():
        print()

        print(
            "Dataset not found."
        )

        print(
            paths["root"]
        )

        sys.exit(1)

    print_report(
        args.version
    )

if __name__ == "__main__":

    main()