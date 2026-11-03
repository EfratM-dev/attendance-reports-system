import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _setup_hebrew_font():
    """Locates and registers Hebrew TTF font to avoid rendering squares or corrupted text."""
    font_name = "HebrewFont"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    possible_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\david.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    ]

    for p in possible_paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(font_name, p))
                return font_name
            except Exception:
                continue

    try:
        pdfmetrics.registerFont(TTFont(font_name, "DejaVuSans.ttf"))
        return font_name
    except Exception:
        return "Helvetica"


def _bidi_text(text: str) -> str:
    """Converts Hebrew text bidirectionally for proper right-to-left alignment in PDF."""
    if not text or not isinstance(text, str):
        return ""

    try:
        from bidi.algorithm import get_display
        return get_display(str(text))
    except ImportError:
        pass

    tokens = re.split(r'([0-9:\./%\-\+]+|[\u0590-\u05fe]+|\s+|[^0-9\u0590-\u05fe\s]+)', str(text))
    tokens = [t for t in tokens if t]

    processed = []
    has_hebrew = any(re.search(r'[\u0590-\u05fe]', t) for t in tokens)

    for t in tokens:
        if re.search(r'[\u0590-\u05fe]', t):
            processed.append(t[::-1])
        else:
            processed.append(t)

    if has_hebrew:
        return "".join(reversed(processed))
    return "".join(processed)


class PdfExportServiceTypeA:
    """PDF export service for Type A reports."""

    @classmethod
    def export(cls, report, filename: str) -> str:
        font_name = _setup_hebrew_font()

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=13,
            leading=16,
            alignment=2,
            textColor=colors.HexColor('#1f2937')
        )

        story = []

        company_label = report.company_name if report.company_name else "לא זוהה"
        title_text = _bidi_text(f"{company_label} - דו\"ח נוכחות")
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 10))

        headers = [
            _bidi_text("שבת"),
            "150%",
            "125%",
            "100%",
            _bidi_text('סה"כ'),
            _bidi_text("הפסקה"),
            _bidi_text("יציאה"),
            _bidi_text("כניסה"),
            _bidi_text("מקום"),
            _bidi_text("יום"),
            _bidi_text("תאריך")
        ]

        table_data = [headers]

        for row in report.rows:
            table_data.append([
                str(getattr(row, 'shabbat', '0.00')),
                str(getattr(row, 'hours_150', '0.00')),
                str(getattr(row, 'hours_125', '0.00')),
                str(getattr(row, 'hours_100', '0.00')),
                str(getattr(row, 'total_hours', '')),
                str(getattr(row, 'break_time', '')),
                str(getattr(row, 'exit_time', '')),
                str(getattr(row, 'entry_time', '')),
                _bidi_text(str(getattr(row, 'location', 'לא זוהה'))),
                _bidi_text(str(getattr(row, 'day_of_week', 'לא זוהה'))),
                _bidi_text(str(getattr(row, 'date', 'לא זוהה')))
            ])

        col_widths = [45, 45, 45, 45, 45, 45, 45, 45, 55, 45, 55]

        main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(main_table)
        story.append(Spacer(1, 10))

        if report.summary:
            s = report.summary
            summary_data = [
                [s.work_days, _bidi_text("ימים")],
                [s.hours, _bidi_text('סה"כ שעות')],
                [s.hours_100, _bidi_text('שעות 100%')],
                [s.hours_125, _bidi_text('שעות 125%')],
                [s.hours_150, _bidi_text('שעות 150%')],
                [s.shabbat_150, _bidi_text('150% שבת')],
                [getattr(s, 'bonus', '0'), _bidi_text("בונוס")],
                [getattr(s, 'travel', '0'), _bidi_text("נסיעות")]
            ]
            summary_table = Table(summary_data, colWidths=[65, 95], hAlign='RIGHT')
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 1.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f1f5f9'))
            ]))
            story.append(summary_table)

        doc.build(story)
        return filename


class PdfExportServiceTypeB:
    """PDF export service for Type B reports."""

    @classmethod
    def export(cls, report, filename: str) -> str:
        font_name = _setup_hebrew_font()

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=13,
            leading=16,
            alignment=2,
            textColor=colors.HexColor('#1f2937')
        )

        story = []

        emp_name = report.employee_name if report.employee_name else "לא זוהה"
        m_label = report.report_month if report.report_month else "לא זוהה"
        header_text = _bidi_text(f"שם העובד: {emp_name} | כרטיס עובד לחודש: {m_label}")
        story.append(Paragraph(header_text, title_style))
        story.append(Spacer(1, 8))

        if report.summary:
            s = report.summary
            summary_data = [
                [s.work_days, _bidi_text('סה"כ ימי עבודה לחודש')],
                [s.hours, _bidi_text('סה"כ שעות חודשיות')],
                [f"₪ {s.hourly_rate}", _bidi_text("מחיר לשעה")],
                [f"₪ {s.total_payment}", _bidi_text('סה"כ לתשלום')]
            ]
            sum_table = Table(summary_data, colWidths=[90, 130], hAlign='RIGHT')
            sum_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f1f5f9')),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(sum_table)
            story.append(Spacer(1, 8))

        headers = [
            _bidi_text("הערות"),
            _bidi_text('סה"כ שעות'),
            _bidi_text("שעת יציאה"),
            _bidi_text("שעת כניסה"),
            _bidi_text("יום בשבוע"),
            _bidi_text("תאריך")
        ]

        table_data = [headers]

        for row in report.rows:
            table_data.append([
                _bidi_text(str(getattr(row, 'notes', '') or '')),
                str(getattr(row, 'total_hours', '')),
                str(getattr(row, 'exit_time', '')),
                str(getattr(row, 'entry_time', '')),
                _bidi_text(str(getattr(row, 'day_of_week', 'לא זוהה'))),
                _bidi_text(str(getattr(row, 'date', 'לא זוהה')))
            ])

        col_widths = [150, 80, 80, 80, 80, 80]

        main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(main_table)

        doc.build(story)
        return filename