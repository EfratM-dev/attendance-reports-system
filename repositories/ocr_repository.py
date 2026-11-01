import pytesseract
from pdf2image import convert_from_path
from typing import Optional


class PDFTextExtractorRepository:
    """מחלקת אחזור האחראית על חילוץ טקסט גולמי מקבצי PDF סרוקים בעברית באמצעות OCR."""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """
        מקבלת נתיב של קובץ PDF סרוק בעברית,
        ממירה כל עמוד לתמונה ומחלצת ממנו את הטקסט בעזרת OCR עם התאמה לשפה העברית.
        """
        try:
            # המרת עמודי ال-PDF לתמונות ברזולוציה גבוהה לשיפור דיוק ה-OCR
            images = convert_from_path(pdf_path, dpi=300)
            full_text = []

            # הגדרות עבור Tesseract לעבודה עם עברית (Page Segmentation Mode 6 - בלוק אחיד של טקסט)
            custom_config = r'--oem 3 --psm 6'

            # מעבר על כל עמוד וחילוץ הטקסט בעברית ובאנגלית
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