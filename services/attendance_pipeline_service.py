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
    Abstract class defining Template Method for processing attendance report.
    Subclasses implement matching, parsing, randomization, metadata, summary, and export steps.
    """

    @staticmethod
    @abstractmethod
    def is_match_type(raw_text: str) -> bool:
        """Step 1: Check raw text match for report type."""
        pass

    @classmethod
    @abstractmethod
    def parse_rows(cls, raw_text: str) -> list:
        """Step 2: Parse and extract rows from raw text."""
        pass

    @classmethod
    @abstractmethod
    def randomize_data(cls, rows: list) -> list:
        """Step 3: Apply deterministic variations preserving original data."""
        pass

    @classmethod
    @abstractmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        """Step 4: Extract metadata (company / employee / month)."""
        pass

    @classmethod
    @abstractmethod
    def calculate_summary(cls, rows: list):
        """Step 5: Calculate total hours and work days summary."""
        pass

    @classmethod
    @abstractmethod
    def create_report_object(cls, rows: list, metadata: dict, summary):
        """Step 6: Construct complete report object."""
        pass

    @staticmethod
    @abstractmethod
    def export_report(report, export_format: str = "pdf", output_filename: str = None) -> str:
        """Step 7: Export report to requested format (PDF / Excel)."""
        pass

    @classmethod
    def process_report(cls, raw_text: str):
        """
        Template Method:
        Manages sequential processing steps in strict order.
        """
        # 1. Parse rows
        parsed_rows = cls.parse_rows(raw_text)

        # 2. Apply variations
        varied_rows = cls.randomize_data(parsed_rows)

        # 3. Extract metadata
        metadata = cls.extract_metadata(raw_text, varied_rows)

        # 4. Calculate summary table
        summary = cls.calculate_summary(varied_rows)

        # 5. Create final report object
        return cls.create_report_object(varied_rows, metadata, summary)


class TypeAHandler(BaseReportHandler):
    """Implementation for Type A report."""

    @staticmethod
    def is_match_type(raw_text: str) -> bool:
        return ReportClassifierService.is_match_type_a(raw_text)

    @classmethod
    def parse_rows(cls, raw_text: str) -> list:
        return AttendanceParserService.parse_rows_type_a(raw_text)

    @classmethod
    def randomize_data(cls, rows: list) -> list:
        return AttendanceMockService.randomize_rows_type_a(rows)

    class TypeAHandler(BaseReportHandler):
        ...

    @classmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        company_name = AttendanceMetadataService.extract_company_name(raw_text)
        return {"company_name": company_name}

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
    """Implementation for Type B report."""

    @staticmethod
    def is_match_type(raw_text: str) -> bool:
        return ReportClassifierService.is_match_type_b(raw_text)

    @classmethod
    def parse_rows(cls, raw_text: str) -> list:
        return AttendanceParserService.parse_rows_type_b(raw_text)

    @classmethod
    def randomize_data(cls, rows: list) -> list:
        return AttendanceMockService.randomize_rows_type_b(rows)

    class TypeBHandler(BaseReportHandler):
        ...

    @classmethod
    def extract_metadata(cls, raw_text: str, rows: list) -> dict:
        month_str = "09/2022"
        for r in rows:
            d = getattr(r, 'date', '')
            if d and '/' in d:
                d_parts = d.split('/')
                if len(d_parts) >= 2 and d_parts[1].isdigit():
                    m_num = f"{int(d_parts[1]):02d}"
                    y_num = f"20{d_parts[2]}" if len(d_parts) > 2 and len(d_parts[2]) == 2 and d_parts[
                        2].isdigit() else (d_parts[2] if len(d_parts) > 2 else "2022")
                    month_str = f"{m_num}/{y_num}"
                    break

        employee_name = AttendanceMetadataService.extract_employee_name(raw_text)
        report_month = AttendanceMetadataService.extract_report_month(rows, raw_text, month_str)
        return {
            "employee_name": employee_name,
            "report_month": report_month or month_str
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
    """Central service managing processing pipeline and export strategy map."""

    def __init__(self):
        self.handlers = {
            "TYPE_A": TypeAHandler,
            "TYPE_B": TypeBHandler
        }

    def process_and_export_report(self, file_url_or_path: str, export_format: str = "pdf",
                                  output_path: str = None) -> str:
        """
        Extracts text, automatically identifies report type, processes data,
        and exports to requested format.
        Output filename appends suffix.
        """
        raw_text = PDFTextExtractorRepository.extract_text_from_pdf(file_url_or_path)
        if not raw_text:
            raise ValueError('לא הצליח לחלץ טקסט מהקובץ הסרוק.')

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