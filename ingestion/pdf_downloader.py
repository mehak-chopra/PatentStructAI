"""
PatentStructAI PDF Downloader.

Downloads a patent PDF and returns detailed metadata about
the download for database persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time

import requests


# ============================================================
# Download Directory
# ============================================================

TEMP_DIR = Path("data/temp")

TEMP_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Download Result
# ============================================================

@dataclass(frozen=True)
class DownloadResult:
    """
    Result of downloading a patent PDF.
    """

    success: bool

    patent_number: str

    pdf_path: Path | None = None

    file_size: int | None = None

    download_time: float | None = None

    error: str | None = None


# ============================================================
# PDF Downloader
# ============================================================

def download_pdf(
    patent_number: str,
    pdf_url: str,
) -> DownloadResult:
    """
    Download a patent PDF.

    Returns
    -------
    DownloadResult
        Detailed information about the download.
    """

    pdf_path = TEMP_DIR / f"{patent_number}.pdf"

    start = time.perf_counter()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/122.0 Safari/537.36"
        )
    }

    try:

        with requests.get(
            pdf_url,
            headers=headers,
            timeout=60,
            stream=True,
        ) as response:

            response.raise_for_status()

            with open(pdf_path, "wb") as file:

                for chunk in response.iter_content(
                    chunk_size=8192
                ):

                    if chunk:

                        file.write(chunk)

        elapsed = time.perf_counter() - start

        file_size = pdf_path.stat().st_size

        print(f"✅ Downloaded {patent_number}")

        return DownloadResult(

            success=True,

            patent_number=patent_number,

            pdf_path=pdf_path,

            file_size=file_size,

            download_time=elapsed,

        )

    except Exception as error:

        if pdf_path.exists():

            pdf_path.unlink(missing_ok=True)

        print(f"❌ Failed {patent_number}")

        print(error)

        return DownloadResult(

            success=False,

            patent_number=patent_number,

            error=str(error),

        )