from database.patent_repository import (
    get_patent_count,
    get_page_count,
    get_failed_patent_count,
    get_country_stats,
    get_average_pages_per_patent,
    get_no_pdf_count,
    get_processed_patent_count
)


def generate_statistics():

    patents = (
        get_patent_count()
    )

    pages = (
        get_page_count()
    )

    failed = (
        get_failed_patent_count()
    )

    no_pdf = (
        get_no_pdf_count()
    )

    processed = (
        get_processed_patent_count()
    )

    avg_pages = (
        get_average_pages_per_patent()
    )

    countries = (
        get_country_stats()
    )

    total_submitted = (
        patents + failed
    )

    print("\n")
    print("=" * 50)
    print("PATENTSTRUCTAI DATASET REPORT")
    print("=" * 50)

    print(
        f"Total Patent Numbers Submitted: "
        f"{total_submitted}"
    )

    print(
        f"Valid Patents: "
        f"{patents}"
    )

    print(
        f"Failed Patents: "
        f"{failed}"
    )

    print(
        f"Patents Without PDF: "
        f"{no_pdf}"
    )

    print(
        f"Successfully Processed Patents: "
        f"{processed}"
    )

    print(
        f"Total Pages: "
        f"{pages}"
    )

    print(
        f"Average Pages/Patent: "
        f"{avg_pages:.2f}"
    )

    print("\n" + "-" * 50)
    print("Countries")
    print("-" * 50)

    for row in countries:

        print(
            f"{row.country}: "
            f"{row.total}"
        )


if __name__ == "__main__":
    generate_statistics()