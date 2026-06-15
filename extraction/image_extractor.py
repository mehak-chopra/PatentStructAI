import fitz
from pathlib import Path


OUTPUT_DIR = Path(
    "data/extracted_images"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

def extract_embedded_images(
    pdf_path,
    patent_number
):

    saved_images = []

    pdf = fitz.open(pdf_path)

    patent_dir = (
        OUTPUT_DIR /
        patent_number
    )

    patent_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for page_index in range(
        len(pdf)
    ):

        page = pdf[
            page_index
        ]

        images = (
            page.get_images(
                full=True
            )
        )

        for image_index, img in enumerate(images):

            xref = img[0]

            base_image = (
                pdf.extract_image(
                    xref
                )
            )

            image_bytes = (
                base_image["image"]
            )

            image_ext = (
                base_image["ext"]
            )

            image_name = (
                f"page_"
                f"{page_index+1}_"
                f"{image_index+1}."
                f"{image_ext}"
            )

            image_path = (
                patent_dir /
                image_name
            )

            with open(
                image_path,
                "wb"
            ) as f:

                f.write(
                    image_bytes
                )

            saved_images.append(
                str(image_path)
            )

    pdf.close()

    return saved_images


def render_pdf_pages(
    pdf_path,
    patent_number
):

    patent_dir = (
        OUTPUT_DIR /
        patent_number
    )

    patent_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    page_records = []

    with fitz.open(pdf_path) as pdf:

        for page_index in range(
            len(pdf)
        ):

            image_path = (
                patent_dir /
                f"page_{page_index + 1}.png"
            )

            if image_path.exists():

                page_records.append(
                    {
                        "page_number":
                            page_index + 1,

                        "image_path":
                            str(image_path)
                    }
                )

                continue

            page = pdf[
                page_index
            ]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    2,
                    2
                )
            )

            pix.save(
                str(image_path)
            )

            page_records.append(
                {
                    "page_number":
                        page_index + 1,

                    "image_path":
                        str(image_path)
                }
            )

    return page_records
