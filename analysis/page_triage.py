"""
Page Triage

Future versions:

V1 - OpenCV Heuristics (deprecated)

V2 - Chemistry Page Classifier

Purpose:
Determine whether a patent page
contains chemistry and assign a
chemistry confidence score.

Outputs:
- chemistry_score
- contains_chemistry
"""

import cv2
import numpy as np
from tqdm import tqdm

from database.patent_repository import (
    get_all_patent_pages,
    update_page_triage
)


def compute_chemistry_score(
    image_path
):

    image = cv2.imread(
        image_path,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        return 0.0

    _, thresh = cv2.threshold(
        image,
        200,
        255,
        cv2.THRESH_BINARY_INV
    )

    num_labels, _, _, _ = (
        cv2.connectedComponentsWithStats(
            thresh,
            connectivity=8
        )
    )

    score = min(
        num_labels / 1000,
        1.0
    )

    return score


def run_triage():

    pages = (
        get_all_patent_pages()
    )

    for page in tqdm(
        pages,
        desc="Page Triage"
    ):

        score = (
            compute_chemistry_score(
                page.image_path
            )
        )

        contains_chemistry = (
            score >= 0.15
        )

        update_page_triage(
            page.id,
            score,
            contains_chemistry
        )

    print(
        "✅ Triage Complete"
    )


if __name__ == "__main__":
    run_triage()

    print(
        "Page triage model "
        "not implemented yet."
    )