import pytesseract
from pdf2image import convert_from_path
from typing import Optional


class PDFTextExtractorRepository:
    """Repository class responsible for extracting raw text from scanned PDF files in Hebrew using OCR."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """
        Receives a path to a scanned Hebrew PDF file,
        converts each page to an image and extracts text using OCR with Hebrew language support.
        """
        try:
            # Convert PDF pages to high-resolution images to improve OCR accuracy
            images = convert_from_path(pdf_path, dpi=300)
            full_text = []

            # Tesseract configuration for Hebrew (Page Segmentation Mode 6 - Uniform block of text)
            custom_config = r'--oem 3 --psm 6'

            # Iterate through pages and extract Hebrew and English text
            for image in images:
                page_text = pytesseract.image_to_string(
                    image,
                    lang='heb+eng',
                    config=custom_config
                )
                full_text.append(page_text)

            return "\n".join(full_text)

        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None