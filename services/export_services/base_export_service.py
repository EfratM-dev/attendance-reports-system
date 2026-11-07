from datetime import date


class BaseExportService:
    """Generic base class encapsulating shared helper methods for exports."""

    @staticmethod
    def _extract_summary_dict(report) -> dict:
        """Extracts dictionary representation of summary object if present."""
        if report and report.summary:
            return report.summary.__dict__
        return {}


class BaseTypeAExportService(BaseExportService):
    """Base export service for Type A reports."""

    @staticmethod
    def _get_headers() -> list:
        return ["תאריך", "כניסה", "יציאה", 'סה"כ שעות', "100%", "125%", "150%", "שבת"]

    @staticmethod
    def _get_rows_data(rows) -> list:
        def format_date(d):
            if isinstance(d, date):
                return d.strftime('%d/%m/%Y')
            return str(d)

        def format_time(t):
            if hasattr(t, 'strftime'):
                return t.strftime('%H:%M')
            return str(t or '')

        return [
            [
                format_date(row.date),
                format_time(row.entry_time),
                format_time(row.exit_time),
                str(row.total_hours), str(row.hours_100),
                str(row.hours_125), str(row.hours_150), str(row.shabbat)
            ]
            for row in rows
        ]

    @staticmethod
    def _get_title(report) -> str:
        company_name = getattr(report, 'company_name', '')
        return f"דו'ח נוכחות - חברה: {company_name}"


class BaseTypeBExportService(BaseExportService):
    """Base export service for Type B reports."""

    @staticmethod
    def _get_headers() -> list:
        return ["תאריך", "כניסה", "יציאה", 'סה"כ שעות']

    @staticmethod
    def _get_rows_data(rows) -> list:
        def format_date(d):
            if isinstance(d, date):
                return d.strftime('%d/%m/%Y')
            return str(d)

        def format_time(t):
            if hasattr(t, 'strftime'):
                return t.strftime('%H:%M')
            return str(t or '')

        return [
            [
                format_date(row.date),
                format_time(row.entry_time),
                format_time(row.exit_time),
                str(row.total_hours)
            ]
            for row in rows
        ]

    @staticmethod
    def _get_title(report) -> str:
        employee_name = getattr(report, 'employee_name', '')
        report_month = getattr(report, 'report_month', '')
        return f"דו'ח נוכחות - עובד: {employee_name} | חודש: {report_month}"