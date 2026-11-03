from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill


class ExcelExportServiceTypeA:
    """Excel export service for Type A attendance reports."""

    @classmethod
    def export(cls, report, filename: str) -> str:
        wb = Workbook()
        ws = wb.active
        ws.title = 'דו"ח נוכחות'
        ws.sheet_view.rightToLeft = True

        ws.append([f"דו\"ח נוכחות - חברה: {report.company_name or 'לא זוהה'}"])
        ws.append([])

        headers = [
            "תאריך", "יום", "מקום", "כניסה", "יציאה", "הפסקה",
            'סה"כ', "100%", "125%", "150%", "שבת"
        ]
        ws.append(headers)

        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=3, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row in report.rows:
            ws.append([
                getattr(row, 'date', 'לא זוהה'),
                getattr(row, 'day_of_week', 'לא זוהה'),
                getattr(row, 'location', 'לא זוהה'),
                getattr(row, 'entry_time', ''),
                getattr(row, 'exit_time', ''),
                getattr(row, 'break_time', ''),
                getattr(row, 'total_hours', ''),
                getattr(row, 'hours_100', '0.00'),
                getattr(row, 'hours_125', '0.00'),
                getattr(row, 'hours_150', '0.00'),
                getattr(row, 'shabbat', '0.00')
            ])

        if report.summary:
            ws.append([])
            ws.append(['סיכום שעות:'])
            s = report.summary
            ws.append(['ימים', s.work_days])
            ws.append(['סה"כ שעות', s.hours])
            ws.append(['שעות 100%', s.hours_100])
            ws.append(['שעות 125%', s.hours_125])
            ws.append(['שעות 150%', s.hours_150])
            ws.append(['שבת 150%', s.shabbat_150])

        wb.save(filename)
        return filename


class ExcelExportServiceTypeB:
    """Excel export service for Type B attendance reports."""

    @classmethod
    def export(cls, report, filename: str) -> str:
        wb = Workbook()
        ws = wb.active
        ws.title = "כרטיס עובד"
        ws.sheet_view.rightToLeft = True

        ws.append([f"שם העובד: {report.employee_name or 'לא זוהה'} | חודש: {report.report_month or 'לא זוהה'}"])
        ws.append([])

        headers = ["תאריך", "יום בשבוע", "שעת כניסה", "שעת יציאה", 'סה"כ שעות', "הערות"]
        ws.append(headers)

        header_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        header_font = Font(name="Arial", size=10, bold=True, color="FFFFFF")

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=3, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row in report.rows:
            ws.append([
                getattr(row, 'date', 'לא זוהה'),
                getattr(row, 'day_of_week', 'לא זוהה'),
                getattr(row, 'entry_time', ''),
                getattr(row, 'exit_time', ''),
                getattr(row, 'total_hours', ''),
                getattr(row, 'notes', '') or ''
            ])

        if report.summary:
            ws.append([])
            ws.append(['סיכום חודשי:'])
            s = report.summary
            ws.append(['סה"כ ימי עבודה לחודש', s.work_days])
            ws.append(['סה"כ שעות חודשיות', s.hours])
            ws.append(['מחיר לשעה', s.hourly_rate])
            ws.append(['סה"כ לתשלום', s.total_payment])

        wb.save(filename)
        return filename