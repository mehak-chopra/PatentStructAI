from pathlib import Path
import shutil
import random


IMAGES_DIR = Path(
    "annotations/images/train"
)

LABELS_DIR = Path(
    "annotations/labels/train"
)

VAL_IMAGES_DIR = Path(
    "annotations/images/val"
)

VAL_LABELS_DIR = Path(
    "annotations/labels/val"
)

VAL_IMAGES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

VAL_LABELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

VAL_RATIO = 0.20


def split_dataset():

    image_files = list(
        IMAGES_DIR.glob("*.png")
    )

    random.shuffle(
        image_files
    )

    val_count = int(
        len(image_files) *
        VAL_RATIO
    )

    val_images = image_files[
        :val_count
    ]

    moved = 0

    for image_file in val_images:

        label_file = (
            LABELS_DIR /
            f"{image_file.stem}.txt"
        )

        shutil.move(
            image_file,
            VAL_IMAGES_DIR /
            image_file.name
        )

        if label_file.exists():

            shutil.move(
                label_file,
                VAL_LABELS_DIR /
                label_file.name
            )

        moved += 1

    print(
        f"✅ Validation Images: "
        f"{moved}"
    )

    print(
        f"✅ Training Images: "
        f"{len(image_files) - moved}"
    )


if __name__ == "__main__":

    split_dataset()