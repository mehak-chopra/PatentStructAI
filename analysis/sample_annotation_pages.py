"""
PatentStructAI Annotation Sampler

Randomly samples unreviewed patent pages for
manual annotation.

Example
-------

python -m analysis.sample_annotation_pages ^
    --version v2

python -m analysis.sample_annotation_pages ^
    --version v2 ^
    --sample-size 300 ^
    --seed 42 ^
    --overwrite
"""

from pathlib import Path
import argparse
import random
import shutil
import sys

from database.review_database import (
    get_reviewed_pages
)


# =====================================================
# Annotation Sampler
# =====================================================

class AnnotationSampler:

    def __init__(

        self,

        version,
        sample_size,
        seed,
        overwrite

    ):

        self.version = version

        self.sample_size = sample_size

        self.seed = seed

        self.overwrite = overwrite

        self.patent_file = Path(
            f"data/chemistry_patent_numbers_{version}.txt"
        )

        self.extracted_images = Path(
            "data/extracted_images"
        )

        self.output_dir = Path(
            f"annotations/chemistry_raw_pages_{version}"
        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        random.seed(

            self.seed

        )

        self.validate()

    # =================================================
    # Validation
    # =================================================

    def validate(self):

        if not self.patent_file.exists():

            print()

            print(
                "Patent list not found."
            )

            print(
                self.patent_file
            )

            sys.exit(1)

        if not self.extracted_images.exists():

            print()

            print(
                "Extracted images directory not found."
            )

            print(
                self.extracted_images
            )

            sys.exit(1)

    # =================================================
    # Load Patent List
    # =================================================

    def load_patents(self):

        with open(

            self.patent_file,

            "r",

            encoding="utf-8"

        ) as file:

            patents = sorted(

                set(

                    line.strip()

                    for line in file

                    if line.strip()

                )

            )

        return patents

    # =================================================
    # Collect Pages
    # =================================================

    def collect_pages(self):

        pages = []

        patents = self.load_patents()

        print()

        print(
            f"Loaded {len(patents)} patents."
        )

        for patent in patents:
            patent_directory = (
                self.extracted_images /
                patent
            )

            if not patent_directory.exists():
                print(
                    f"Missing folder : {patent}"
                )
                continue

            pages.extend(
                sorted(
                    patent_directory.glob(
                        "*.png"
                    )
                )
            )

        print(
            f"Collected {len(pages)} pages."
        )

        return pages

    # =================================================
    # Prepare Output Directory
    # =================================================

    def prepare_output_directory(self):

        if self.overwrite:

            for file in self.output_dir.glob(
                "*.png"
            ):

                file.unlink()

    # =================================================
    # Get Available Pages
    # =================================================

    def get_available_pages(

        self,
        pages

    ):

        reviewed_pages = (

            get_reviewed_pages()

        )

        available_pages = []

        for page in pages:

            identifier = (

                f"{page.parent.name}_{page.name}"

            )

            if identifier not in reviewed_pages:

                available_pages.append(
                    page
                )

        print()

        print(
            f"Already Reviewed : {len(reviewed_pages)}"
        )

        print(
            f"Available Pages  : {len(available_pages)}"
        )

        return available_pages


    # clear previous sampling batch.
    # chemistry_raw_pages_v2 is a temporary review folder.
    # move confirmed chemistry pages to
    # annotations/confirmed_chemistry_pages_v2
    # before running the sampler again.

        # =================================================
    # Sample Pages
    # =================================================

    def sample_pages(

        self,
        available_pages

    ):

        if not available_pages:

            print()

            print(
                "No new pages available for sampling."
            )

            return []

        sample_count = min(

            self.sample_size,

            len(available_pages)

        )

        sampled_pages = random.sample(

            available_pages,

            sample_count

        )

        print()

        print(

            f"Sampling {sample_count} pages "

            f"from {len(available_pages)} "

            f"available pages."

        )

        return sampled_pages

    # =================================================
    # Copy Sampled Pages
    # =================================================

    def copy_pages(

        self,
        sampled_pages

    ):

        if not sampled_pages:

            return

        copied = 0

        for page in sampled_pages:

            destination = (

                self.output_dir /

                f"{page.parent.name}_{page.name}"

            )

            shutil.copy2(

                page,

                destination

            )

            copied += 1

        print()

        print(

            f"Pages Sampled : {copied}"

        )

        print(

            f"Output Folder :"

        )

        print(

            self.output_dir

        )

    # =================================================
    # Run
    # =================================================

    def run(self):

        print()

        print("=" * 60)

        print(
            "PatentStructAI Annotation Sampler"
        )

        print("=" * 60)

        self.prepare_output_directory()

        pages = self.collect_pages()

        available_pages = self.get_available_pages(
            pages
        )

        sampled_pages = self.sample_pages(
            available_pages
        )

        self.copy_pages(
            sampled_pages
        )

        print()

        print(
            "Annotation sampling completed."
        )


# =====================================================
# Main
# =====================================================

def main():

    parser = argparse.ArgumentParser(

        description=(

            "Sample unreviewed patent pages "

            "for manual annotation."

        )

    )

    parser.add_argument(

        "--version",

        default="v2",

        help=(

            "Patent list version "

            "(v1, v2, v3...)"

        )

    )

    parser.add_argument(

        "--sample-size",

        type=int,

        default=300,

        help=(

            "Number of pages "

            "to sample."

        )

    )

    parser.add_argument(

        "--seed",

        type=int,

        default=42,

        help=(

            "Random seed."

        )

    )

    parser.add_argument(

        "--overwrite",

        action="store_true",

        help=(

            "Clear previous sampled "

            "pages before sampling."

        )

    )

    args = parser.parse_args()

    sampler = AnnotationSampler(

        version=args.version,

        sample_size=args.sample_size,

        seed=args.seed,

        overwrite=args.overwrite

    )

    sampler.run()


if __name__ == "__main__":

    main()