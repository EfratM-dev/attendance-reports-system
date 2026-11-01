class BaseExportService:
    """מחלקת בסיס גנרית המרכזת פעולות עזר משותפות לכל סוגי הייצוא."""

    @staticmethod
    def _extract_summary_dict(report) -> dict:
        """מחזיר את מילון הנתונים מתוך אובייקט הסיכום של הדו"ח, אם קיים."""
        if report and report.summary:
            return report.summary.__dict__
        return {}


class BaseTypeAExportService(BaseExportService):
    """מחלקת בסיס ייעודית עבור דו"חות מסוג A (הכנת נתונים, כותרות וכותרת ראשית)."""

    @staticmethod
    def _get_headers() -> list:
        return ["תאריך", "כניסה", "יציאה", "סה\"כ שעות", "100%", "125%", "150%", "שבת"]

    @staticmethod
    def _get_rows_data(rows) -> list:
        return [
            [
                str(row.date), str(row.entry_time), str(row.exit_time),
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
    """מחלקת בסיס ייעודית עבור דו"חות מסוג B (הכנת נתונים, כותרות וכותרת ראשית)."""

    @staticmethod
    def _get_headers() -> list:
        return ["תאריך", "כניסה", "יציאה", "סה\"כ שעות"]

    @staticmethod
    def _get_rows_data(rows) -> list:
        return [
            [
                str(row.date), str(row.entry_time), str(row.exit_time), str(row.total_hours)
            ]
            for row in rows
        ]

    @staticmethod
    def _get_title(report) -> str:
        employee_name = getattr(report, 'employee_name', '')
        report_month = getattr(report, 'report_month', '')
        return f"דו'ח נוכחות - עובד: {employee_name} | חודש: {report_month}"