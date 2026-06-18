from pathlib import Path
import shutil


IMAGE_FOLDERS = [
    Path("annotations/confirmed_chemistry_pages"),
    Path("annotations/raw_pages")
]

EXPORTED_LABELS = Path(
    "annotations/labels/train"
)

YOLO_IMAGES = Path(
    "annotations/images/train"
)

YOLO_IMAGES.mkdir(
    parents=True,
    exist_ok=True
)

copied = 0

for label_file in EXPORTED_LABELS.glob(
    "*.txt"
):

    image_name = (
        label_file.stem + ".png"
    )

    image_file = None

    for folder in IMAGE_FOLDERS:

        candidate = (
            folder /
            image_name
        )

        if candidate.exists():

            image_file = candidate
            break

    if image_file is None:

        print(
            f"Missing image: "
            f"{image_name}"
        )

        continue

    shutil.copy2(
        image_file,
        YOLO_IMAGES / image_name
    )

    copied += 1

print(
    f"✅ Copied "
    f"{copied} images"
)