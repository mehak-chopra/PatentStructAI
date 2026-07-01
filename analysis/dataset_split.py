from pathlib import Path
import random
import shutil
import argparse

# =====================================================
# Usage
# =====================================================
#
# Create a dataset split:
#
# python -m analysis.dataset_split --version v2
#
# Replace "v2" with any dataset version (v3, v4, ...).
#
# =====================================================


# =====================================================
# Dataset Configuration
# =====================================================

parser = argparse.ArgumentParser(
    description="Create a YOLO dataset split."
)

parser.add_argument(
    "--version",
    required=True,
    help="Dataset version (v2, v3, ...)"
)

args = parser.parse_args()

DATASET_VERSION = args.version

SOURCE_IMAGES = Path(
    f"annotations/confirmed_chemistry_pages_{DATASET_VERSION}"
)

SOURCE_LABELS = Path(
    f"annotations/confirmed_chemistry_pages_{DATASET_VERSION}/labels"
)

OUTPUT_ROOT = Path(
    f"annotations/datasets/{DATASET_VERSION}"
)

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

if not (
    abs(
        (
            TRAIN_RATIO +
            VAL_RATIO +
            TEST_RATIO
        ) - 1.0
    ) < 1e-9
):

    raise ValueError(
        "Dataset split ratios must sum to 1."
    )

RANDOM_SEED = 42


# =====================================================
# Helper Functions
# =====================================================

def create_directories():

    for split in [
        "train",
        "val",
        "test"
    ]:

        (
            OUTPUT_ROOT /
            "images" /
            split
        ).mkdir(
            parents=True,
            exist_ok=True
        )

        (
            OUTPUT_ROOT /
            "labels" /
            split
        ).mkdir(
            parents=True,
            exist_ok=True
        )


def collect_dataset():

    image_files = sorted(
        SOURCE_IMAGES.glob("*.png")
    )

    dataset = []

    skipped = 0

    for image in image_files:

        label = (
            SOURCE_LABELS /
            f"{image.stem}.txt"
        )

        if not label.exists():

            skipped += 1
            continue

        dataset.append(
            (
                image,
                label
            )
        )

    print()

    print("=" * 45)
    print("Dataset Scan")
    print("=" * 45)

    print(
        f"Dataset Version : {DATASET_VERSION}"
    )
    
    print()

    print(
        f"Images found: {len(image_files)}"
    )

    print(
        f"Annotated images: {len(dataset)}"
    )

    print(
        f"Skipped (no label): {skipped}"
    )

    return dataset


def split_dataset(dataset):

    random.seed(
        RANDOM_SEED
    )

    random.shuffle(
        dataset
    )

    total = len(dataset)

    train_end = int(
        total *
        TRAIN_RATIO
    )

    val_end = train_end + int(
        total *
        VAL_RATIO
    )

    train = dataset[
        :train_end
    ]

    val = dataset[
        train_end:val_end
    ]

    test = dataset[
        val_end:
    ]

    return (
        train,
        val,
        test
    )


def copy_split(
    split_name,
    files
):

    image_output = (
        OUTPUT_ROOT /
        "images" /
        split_name
    )

    label_output = (
        OUTPUT_ROOT /
        "labels" /
        split_name
    )

    for image, label in files:

        shutil.copy2(
            image,
            image_output /
            image.name
        )

        shutil.copy2(
            label,
            label_output /
            label.name
        )


def create_data_yaml():

    yaml_path = (
        OUTPUT_ROOT /
        "data.yaml"
    )

    yaml_text = f"""path: {OUTPUT_ROOT.as_posix()}

train: images/train
val: images/val
test: images/test

names:
  0: chemistry_structure
"""

    yaml_path.write_text(
        yaml_text,
        encoding="utf-8"
    )


def print_summary(
    train,
    val,
    test
):

    print()

    print("=" * 45)
    print("Dataset Split Summary")
    print("=" * 45)

    print(
        f"Dataset Version : {DATASET_VERSION}"
    )

    print()

    print(
        f"Training images   : {len(train)}"
    )

    print(
        f"Validation images : {len(val)}"
    )

    print(
        f"Testing images    : {len(test)}"
    )

    print()

    print(
        f"Dataset created at:"
    )

    print(
        OUTPUT_ROOT
    )

def clear_output_directory():

    if not OUTPUT_ROOT.exists():
        return

    for split in [
        "train",
        "val",
        "test"
    ]:

        image_dir = (
            OUTPUT_ROOT /
            "images" /
            split
        )

        label_dir = (
            OUTPUT_ROOT /
            "labels" /
            split
        )

        for file in image_dir.glob("*.png"):
            file.unlink()

        for file in label_dir.glob("*.txt"):
            file.unlink()


# =====================================================
# Main
# =====================================================

def main():

    create_directories()

    clear_output_directory()

    dataset = collect_dataset()

    if not dataset:

        print(
            "No annotated images found."
        )

        return

    train, val, test = split_dataset(
        dataset
    )

    copy_split(
        "train",
        train
    )

    copy_split(
        "val",
        val
    )

    copy_split(
        "test",
        test
    )

    create_data_yaml()

    print_summary(
        train,
        val,
        test
    )


if __name__ == "__main__":
    main()