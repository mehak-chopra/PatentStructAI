import requests
from bs4 import BeautifulSoup


def fetch_patent_metadata(
    patent_number
):

    url = (
        f"https://patents.google.com/"
        f"patent/{patent_number}/en"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/122.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:

        raise Exception(
            f"Failed to fetch patent page: "
            f"{response.status_code}"
        )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    title_tag = soup.find(
        "span",
        attrs={
            "itemprop": "title"
        }
    )

    pdf_tag = soup.find(
        "a",
        attrs={
            "itemprop": "pdfLink"
        }
    )

    title = (
        title_tag.text.strip()
        if title_tag
        else None
    )

    pdf_url = (
        pdf_tag["href"]
        if pdf_tag
        else None
    )

    country = (
        patent_number[:2]
    )

    return {
        "patent_number":
            patent_number,

        "title":
            title,

        "pdf_url":
            pdf_url,

        "country":
            country
    }
