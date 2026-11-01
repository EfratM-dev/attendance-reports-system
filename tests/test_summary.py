import pytest
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB
from services.attendance_summary_service import AttendanceSummaryService


def test_calculate_summary_type_a():
    rows = [
        AttendanceRowTypeA("01/10/2022", "יום ראשון", "משרד", "08:00", "16:00", "00:30", "7.50", "7.50", "0.00", "0.00", "0.00"),
        AttendanceRowTypeA("02/10/2022", "יום שני", "משרד", "08:00", "17:00", "00:30", "8.50", "8.00", "0.50", "0.00", "0.00"),
    ]
    summary = AttendanceSummaryService.calculate_summary_type_a(rows)
    assert int(summary.work_days) == 2
    assert float(summary.hours_100) == 15.5
    assert float(summary.hours_125) == 0.5


def test_calculate_summary_type_b():
    rows = [
        AttendanceRowTypeB("1/9/22", "חמישי", "08:30", "12:00", "3.50", ""),
        AttendanceRowTypeB("2/9/22", "שישי", "08:30", "12:00", "3.50", ""),
    ]
    summary = AttendanceSummaryService.calculate_summary_type_b(rows)
    assert int(summary.work_days) == 2
    assert float(summary.hours) == 7.0