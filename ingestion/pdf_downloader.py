from pathlib import Path
import requests


TEMP_DIR = Path(
    "data/temp"
)

TEMP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def download_pdf(
    patent_id,
    patent_number,
    pdf_url
):

    pdf_path = (
        TEMP_DIR /
        f"{patent_number}.pdf"
    )

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/122.0 Safari/537.36"
            )
        }

        with requests.get(
            pdf_url,
            headers=headers,
            timeout=60,
            stream=True
        ) as response:

            response.raise_for_status()

            with open(
                pdf_path,
                "wb"
            ) as f:

                for chunk in response.iter_content(
                    chunk_size=8192
                ):

                    if chunk:

                        f.write(
                            chunk
                        )

        print(
            f"✅ Downloaded "
            f"{patent_number}"
        )

        return pdf_path

    except Exception as e:

        print(
            f"❌ Failed "
            f"{patent_number}"
        )

        print(e)

        return None