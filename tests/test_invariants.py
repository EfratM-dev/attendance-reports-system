import pytest
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB
from services.attendance_mock_service import AttendanceMockService


def test_randomize_rows_type_a_invariants():
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

    updated_rows = AttendanceMockService.randomize_rows_type_a([original_row])
    row = updated_rows[0]

    # אינווריאנט 1: שעת יציאה מאוחרת משעת כניסה
    entry_h, entry_m = map(int, row.entry_time.split(':'))
    exit_h, exit_m = map(int, row.exit_time.split(':'))
    assert (exit_h * 60 + exit_m) > (entry_h * 60 + entry_m)

    # אינווריאנט 2: שימור יום השבוע והמקום מקובץ המקור
    assert row.day_of_week == "יום ראשון"
    assert row.location == "גליליון"

    # אינווריאנט 3: תקינות סך השעות
    assert float(row.total_hours) >= 0.0


def test_randomize_rows_type_b_invariants():
    original_row = AttendanceRowTypeB(
        date="1/9/22",
        day_of_week="חמישי",
        entry_time="08:30",
        exit_time="12:00",
        total_hours="3.50",
        notes="ערב חג"
    )

    updated_rows = AttendanceMockService.randomize_rows_type_b([original_row])
    row = updated_rows[0]

    # אינווריאנט 1: שעת יציאה מאוחרת משעת כניסה
    entry_h, entry_m = map(int, row.entry_time.split(':'))
    exit_h, exit_m = map(int, row.exit_time.split(':'))
    assert (exit_h * 60 + exit_m) > (entry_h * 60 + entry_m)

    # אינווריאנט 2: שימור ההערות מקובץ המקור
    assert row.notes == "ערב חג"