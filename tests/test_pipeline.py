import pytest
from services.attendance_pipeline_service import TypeAHandler, TypeBHandler


def test_type_a_handler_process_flow():
    raw_text = """
    נ.ע. הנשר כח אדם בע"מ - דו"ח נוכחות
    תאריך | יום | מקום | כניסה | יציאה | הפסקה | סה"כ | 100% | 125% | 150% | שבת
    02/10/2022 | יום ראשון | גליליון | 08:00 | 15:00 | 00:30 | 6.50 | 6.50 | 0.00 | 0.00 | 0.00
    """
    report = TypeAHandler.process_report(raw_text)
    assert report.report_type == "TYPE_A"
    assert len(report.rows) > 0
    assert report.summary is not None


def test_type_b_handler_process_flow():
    raw_text = """
    שם העובד: ישראל ישראלי | כרטיס עובד לחודש: 09/2022
    תאריך | יום בשבוע | שעת כניסה | שעת יציאה | סה"כ שעות | הערות
    1/9/22 | חמישי | 8:30 | 12:00 | 3.50 | 
    """
    report = TypeBHandler.process_report(raw_text)
    assert report.report_type == "TYPE_B"
    assert len(report.rows) > 0
    assert report.summary is not None