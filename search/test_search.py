"""
Developer utility for testing PatentStructAI search.

Examples
--------

Search using SMILES (default: Exact + Substructure)

python -m search.test_search --smiles "CCO"

SMILES

python test_search.py `
    --smiles "CCO"

Image

python test_search.py `
    --image inputs/image.png

Exact only

python test_search.py `
    --mode exact `
    --smiles "CCO"

Similarity only

python test_search.py `
    --mode similarity `
    --smiles "CCO"

Substructure only

python test_search.py `
    --mode substructure `
    --smiles "CCO"

Ruxolitinib structure
    
python -m search.test_search --smiles "N#CC[C@H](C1CCCC1)n1cc(-c2ncnc3[nH]ccc23)cn1"

Viewing image in terminal

outputs/AU2023318885A1/structures/page_21/structure_002.png


"""

from __future__ import annotations

import argparse
from pathlib import Path

from search.search_engine import (
    SearchEngine,
)

from reports.html_report import (
    HTMLReport,
)

# ============================================================
# Result Printer
# ============================================================

def print_results(
    results,
):
    """
    Pretty-print search results.
    """

    if not results:

        print()

        print("No matches found.")

        return

    print()

    print("=" * 80)

    print(f"Matches Found : {len(results)}")

    print("=" * 80)

    for index, result in enumerate(

        results,

        start=1,

    ):

        print()

        print(f"[{index}]")

        print(

            f"Patent Number : {result.patent_number}"

        )

        print(

            f"Title         : {result.patent_title}"

        )

        print(

            f"Search Type   : {result.search_type.value}"

        )

        print(

            f"Page          : {result.page_number}"

        )

        print(

            f"Crop          : {result.crop_index}"

        )

        print(

            f"Structure ID  : {result.structure_id}"

        )

        print(

            f"SMILES        : {result.canonical_smiles}"

        )

        if result.similarity_score is not None:

            print(

                "Similarity    : "

                f"{result.similarity_score:.3f}"

            )

        print(

            f"Image         : {result.image_path}"

        )

        print("-" * 80)


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(

        description=(
            "PatentStructAI Search Tester"
        )

    )

    # --------------------------------------------------------
    # Input
    # --------------------------------------------------------

    parser.add_argument(

        "--smiles",

        help=(
            "SMILES query."
        ),

    )

    parser.add_argument(

        "--image",

        type=Path,

        help=(
            "Chemical structure image."
        ),

    )

    # --------------------------------------------------------
    # Search Mode
    # --------------------------------------------------------

    parser.add_argument(

        "--mode",

        default="all",

        choices=[

            "all",

            "exact",

            "substructure",

            "similarity",

        ],

        help=(
            "Search mode."
        ),

    )

    # --------------------------------------------------------
    # Similarity Options
    # --------------------------------------------------------

    parser.add_argument(

        "--threshold",

        type=float,

        default=0.50,

        help=(
            "Similarity threshold."
        ),

    )

    parser.add_argument(

        "--top-k",

        type=int,

        default=10,

        help=(
            "Maximum number of similarity matches."
        ),

    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Validate Input
    # --------------------------------------------------------

    if args.smiles is None and args.image is None:

        parser.error(

            "Provide either --smiles or --image."

        )

    if args.smiles is not None and args.image is not None:

        parser.error(

            "Provide only one of --smiles or --image."

        )

    # --------------------------------------------------------
    # Build Search Engine
    # --------------------------------------------------------

    engine = SearchEngine()

    query = (

        args.image

        if args.image is not None

        else args.smiles

    )

    # --------------------------------------------------------
    # Execute Search
    # --------------------------------------------------------

    if args.mode == "all":

        results = engine.search(
            query
        )

    elif args.mode == "exact":

        results = engine.exact(
            query
        )

    elif args.mode == "substructure":

        results = engine.substructure(
            query
        )

    else:

        results = engine.similarity(

            query,

            threshold=args.threshold,

            top_k=args.top_k,

        )

    # Generate HTML report
    report = HTMLReport()

    report_path = report.save(

        results=results,

        query=query,

        search_type=args.mode,

    )

    from collections import Counter


    print_results(
        results
    )

    print(
        Counter(
            result.search_type.value
            for result in results
        )
    )

    print()

    print(

        f"HTML report saved to:\n{report_path}"

    )


if __name__ == "__main__":

    main()