from pathlib import Path


LABELS_DIR = Path(
    "annotations/labels/train"
)


def generate_annotation_statistics():

    label_files = list(
        LABELS_DIR.glob("*.txt")
    )

    total_images = len(
        label_files
    )

    empty_pages = 0

    total_annotations = 0

    max_annotations = 0

    max_page = None

    min_annotations = float(
        "inf"
    )

    min_page = None

    for label_file in label_files:

        with open(
            label_file,
            "r",
            encoding="utf-8"
        ) as f:

            annotations = [
                line.strip()
                for line in f
                if line.strip()
            ]

        annotation_count = len(
            annotations
        )

        if annotation_count == 0:

            empty_pages += 1

        total_annotations += (
            annotation_count
        )

        if (
            annotation_count >
            max_annotations
        ):

            max_annotations = (
                annotation_count
            )

            max_page = (
                label_file.name
            )

        if (
            annotation_count <
            min_annotations
        ):

            min_annotations = (
                annotation_count
            )

            min_page = (
                label_file.name
            )

    avg_annotations = 0

    if total_images > 0:

        avg_annotations = (
            total_annotations /
            total_images
        )

    if min_annotations == float(
        "inf"
    ):

        min_annotations = 0

    print("\n")
    print("=" * 50)
    print(
        "ANNOTATION DATASET REPORT"
    )
    print("=" * 50)

    print(
        f"Annotated Pages: "
        f"{total_images}"
    )

    print(
        f"Total Structures: "
        f"{total_annotations}"
    )

    print(
        f"Average Structures/Page: "
        f"{avg_annotations:.2f}"
    )

    print(
        f"Empty Pages: "
        f"{empty_pages}"
    )

    print(
        f"Most Crowded Page: "
        f"{max_page}"
    )

    print(
        f"Structures On Page: "
        f"{max_annotations}"
    )

    print(
        f"Least Crowded Page: "
        f"{min_page}"
    )

    print(
        f"Structures On Page: "
        f"{min_annotations}"
    )

    print("=" * 50)


if __name__ == "__main__":

    generate_annotation_statistics()