import os
from abc import ABC, abstractmethod
from repositories.ocr_repository import PDFTextExtractorRepository
from services.report_classifier_service import ReportClassifierService
from services.attendance_parser_service import AttendanceParserService
from services.attendance_mock_service import AttendanceMockService
from services.attendance_summary_service import AttendanceSummaryService
from services.attendance_metadata_service import AttendanceMetadataService
from models.attendance_report import AttendanceReportTypeA, AttendanceReportTypeB
from services.export_services.pdf_export_service import PdfExportServiceTypeA, PdfExportServiceTypeB
from services.export_services.excel_export_service import ExcelExportServiceTypeA, ExcelExportServiceTypeB


class BaseReportHandler(ABC):
    """
    מחלקה אבסטרקטית המגדירה Template Method לתהליך עיבוד דוח נוכחות.
    כל סוג דוח (TypeA, TypeB...) מחויב לממש את כל תת-הפונקציות:
    זיהוי, פרסור, שינויים הגיוניים, מטא-דאטה, סיכום וייצוא.
    """

    @staticmethod
    @abstractmethod
    def is_match_type(raw_text: str) -> bool:
        """שלב 1: בדיקת התאמת הטקסט הגולמי לסוג הדוח."""
        pass

    @classmethod
    @abstractmethod
    def parse_rows(cls, raw_text: str) -> list:
        """שלב 2: ניתוח וחילוץ שורות הנוכחות מתוך הטקסט הגולמי."""
        pass

    @classmethod
    @abstractmethod
    def randomize_data(cls, rows: list) -> list:
        """שלב 3: החלת וריאציה הגיונית ודטרמיניסטית על השורות תוך שימור נתוני המקור."""
        pass

    @classmethod
    @abstractmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        """שלב 4: חילוץ נתוני מטא-דאטה (שם חברה / שם עובד / חודש)."""
        pass

    @classmethod
    @abstractmethod
    def calculate_summary(cls, rows: list):
        """שלב 5: חישוב נתוני סיכום השעות וימי העבודה."""
        pass

    @classmethod
    @abstractmethod
    def create_report_object(cls, rows: list, metadata: dict, summary):
        """שלב 6: הרכבת אובייקט הדו"ח השלם."""
        pass

    @staticmethod
    @abstractmethod
    def export_report(report, export_format: str = "pdf", output_filename: str = None) -> str:
        """שלב 7: ייצוא הדו"ח לפורמט המבוקש (PDF / Excel)."""
        pass

    @classmethod
    def process_report(cls, raw_text: str):
        """
        Template Method (תבנית התהליך):
        מנהלת את רצף העיבוד בסדר קבוע ומחייב לכל סוג דוח,
        מבלי שסוג דוח ספציפי יוכל לשבש את סדר השלבים.
        """
        # 1. פרסור השורות
        parsed_rows = cls.parse_rows(raw_text)

        # 2. החלת וריאציות הגיוניות
        varied_rows = cls.randomize_data(parsed_rows)

        # 3. חילוץ מטא-דאטה
        metadata = cls.extract_metadata(raw_text, varied_rows)

        # 4. חישוב טבלת סיכום
        summary = cls.calculate_summary(varied_rows)

        # 5. יצירת אובייקט הדוח הסופי
        return cls.create_report_object(varied_rows, metadata, summary)


class TypeAHandler(BaseReportHandler):
    """מימוש מלא עבור דו"ח מסוג A."""

    @staticmethod
    def is_match_type(raw_text: str) -> bool:
        return ReportClassifierService.is_match_type_a(raw_text)

    @classmethod
    def parse_rows(cls, raw_text: str) -> list:
        return AttendanceParserService.parse_rows_type_a(raw_text)

    @classmethod
    def randomize_data(cls, rows: list) -> list:
        return AttendanceMockService.randomize_rows_type_a(rows)

    @classmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        temp_report = AttendanceReportTypeA(report_type="TYPE_A", company_name="", rows=rows, summary=None)
        AttendanceMetadataService.process_metadata_type_a(temp_report, raw_text, "")
        return {"company_name": temp_report.company_name}

    @classmethod
    def calculate_summary(cls, rows: list):
        return AttendanceSummaryService.calculate_summary_type_a(rows)

    @classmethod
    def create_report_object(cls, rows: list, metadata: dict, summary) -> AttendanceReportTypeA:
        return AttendanceReportTypeA(
            report_type="TYPE_A",
            company_name=metadata.get("company_name", "לא זוהה"),
            rows=rows,
            summary=summary
        )

    @staticmethod
    def export_report(report, export_format: str = "pdf", output_filename: str = None) -> str:
        format_lower = export_format.lower()
        os.makedirs("outputs", exist_ok=True)

        if format_lower in ["excel", "xlsx"]:
            filename = output_filename or os.path.join("outputs", "attendance_report_a_output.xlsx")
            return ExcelExportServiceTypeA.export(report, filename)

        elif format_lower in ["pdf"]:
            filename = output_filename or os.path.join("outputs", "attendance_report_a_output.pdf")
            return PdfExportServiceTypeA.export(report, filename)

        else:
            raise ValueError(f"פורמט ייצוא לא נתמך: {export_format}")


class TypeBHandler(BaseReportHandler):
    """מימוש מלא עבור דו"ח מסוג B."""

    @staticmethod
    def is_match_type(raw_text: str) -> bool:
        return ReportClassifierService.is_match_type_b(raw_text)

    @classmethod
    def parse_rows(cls, raw_text: str) -> list:
        return AttendanceParserService.parse_rows_type_b(raw_text)

    @classmethod
    def randomize_data(cls, rows: list) -> list:
        return AttendanceMockService.randomize_rows_type_b(rows)

    @classmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        # הפקת מספר חודש מדויק (למשל 1/9/22 -> 09/2022)
        month_str = "09/2022"
        for r in rows:
            d = getattr(r, 'date', '')
            if d and '/' in d:
                d_parts = d.split('/')
                if len(d_parts) >= 2 and d_parts[1].isdigit():
                    m_num = f"{int(d_parts[1]):02d}"
                    y_num = f"20{d_parts[2]}" if len(d_parts) > 2 and len(d_parts[2]) == 2 and d_parts[2].isdigit() else (d_parts[2] if len(d_parts) > 2 else "2022")
                    month_str = f"{m_num}/{y_num}"
                    break

        temp_report = AttendanceReportTypeB(report_type="TYPE_B", employee_name="", report_month=month_str,
                                            rows=rows, summary=None)
        AttendanceMetadataService.process_metadata_type_b(temp_report, raw_text, month_str)
        return {
            "employee_name": temp_report.employee_name,
            "report_month": temp_report.report_month or month_str
        }

    @classmethod
    def calculate_summary(cls, rows: list):
        return AttendanceSummaryService.calculate_summary_type_b(rows)

    @classmethod
    def create_report_object(cls, rows: list, metadata: dict, summary) -> AttendanceReportTypeB:
        return AttendanceReportTypeB(
            report_type="TYPE_B",
            employee_name=metadata.get("employee_name", "לא זוהה"),
            report_month=metadata.get("report_month", "לא זוהה"),
            rows=rows,
            summary=summary
        )

    @staticmethod
    def export_report(report, export_format: str = "pdf", output_filename: str = None) -> str:
        format_lower = export_format.lower()
        os.makedirs("outputs", exist_ok=True)

        if format_lower in ["excel", "xlsx"]:
            filename = output_filename or os.path.join("outputs", "attendance_report_b_output.xlsx")
            return ExcelExportServiceTypeB.export(report, filename)

        elif format_lower in ["pdf"]:
            filename = output_filename or os.path.join("outputs", "attendance_report_b_output.pdf")
            return PdfExportServiceTypeB.export(report, filename)

        else:
            raise ValueError(f"פורמט ייצוא לא נתמך: {export_format}")


class AttendancePipelineService:
    """שירות מרכזי המנהל את צינור העיבוד והייצוא באמצעות מילון אסטרטגיות."""

    def __init__(self):
        self.handlers = {
            "TYPE_A": TypeAHandler,
            "TYPE_B": TypeBHandler
        }

    def process_and_export_report(self, file_url_or_path: str, export_format: str = "pdf",
                                  output_path: str = None) -> str:
        """
        מחלץ את הטקסט, מזהה את סוג הדו"ח באופן אוטומטי, מעבד אותו
        ומייצא לקובץ בפורמט המבוקש לפי בחירת המשתמש.
        דרישה 9: שם קובץ הפלט מקבל את שם קובץ הקלט בתוספת המילה output.
        """
        raw_text = PDFTextExtractorRepository.extract_text_from_pdf(file_url_or_path)
        if not raw_text:
            raise ValueError('לא הצליח לחלץ טקסט מהקובץ הסרוק.')

        # הפקת סיומת ושם קובץ הפלט באמצעות if / elif
        if not output_path:
            format_lower = export_format.lower()
            if format_lower in ["excel", "xlsx"]:
                ext = ".xlsx"
            elif format_lower in ["pdf"]:
                ext = ".pdf"
            else:
                raise ValueError(f"פורמט ייצוא לא נתמך: {export_format}")

            base_name = os.path.splitext(os.path.basename(file_url_or_path))[0]
            output_path = os.path.join("outputs", f"{base_name}_output{ext}")

        for handler in self.handlers.values():
            if handler.is_match_type(raw_text):
                report_obj = handler.process_report(raw_text)
                return handler.export_report(report_obj, export_format, output_path)

        raise ValueError('לא נמצאה התאמה לאף סוג דו"ח מוכר.')