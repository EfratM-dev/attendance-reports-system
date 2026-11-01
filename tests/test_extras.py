import pytest
import copy
from services.attendance_metadata_service import AttendanceMetadataService
from models.attendance_report import AttendanceReportTypeA, AttendanceReportTypeB
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB
from services.attendance_mock_service import AttendanceMockService


def test_metadata_extraction_type_a():
    raw_text = """
    נ.ע. הנשר כח אדם בע"מ - דו"ח נוכחות
    02/10/2022 | יום ראשון | גליליון | 08:00 | 15:00
    """
    report = AttendanceReportTypeA(report_type="TYPE_A", company_name="", rows=[])
    updated_report = AttendanceMetadataService.process_metadata_type_a(report, raw_text, "")
    assert "הנשר" in updated_report.company_name


def test_metadata_extraction_type_b():
    raw_text = """
    שם העובד: ישראל ישראלי
    כרטיס עובד לחודש: 09/2022
    1/9/22 | חמישי | 8:30 | 12:00
    """
    report = AttendanceReportTypeB(report_type="TYPE_B", employee_name="", report_month="", rows=[])
    updated_report = AttendanceMetadataService.process_metadata_type_b(report, raw_text, "09/2022")
    assert "ישראל ישראלי" in updated_report.employee_name
    assert updated_report.report_month == "09/2022"


def test_determinism_and_immutability_type_a():
    original_row = AttendanceRowTypeA(
        date="02/10/2022",
        day_of_week="יום ראשון",
        location="גליליון",
        entry_time="08:00",
        exit_time="15:00",
        break_time="00:30",
        total_hours="6.50",
        hours_100="6.50",
        hours_125="0.00",
        hours_150="0.00",
        shabbat="0.00"
    )

    original_day = original_row.day_of_week
    original_location = original_row.location

    updated_rows = AttendanceMockService.randomize_rows_type_a([original_row])

    assert updated_rows[0].day_of_week == original_day
    assert updated_rows[0].location == original_location