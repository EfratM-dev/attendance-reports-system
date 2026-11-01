import pytest
from services.attendance_parser_service import AttendanceParserService


def test_parse_rows_type_a():
    raw_text = """
    02/10/2022 | יום ראשון | גליליון | 08:00 | 15:00 | 00:30 | 6.50 | 6.50 | 0.00 | 0.00 | 0.00
    07/10/2022 | יום שישי | גן | 08:00 | 15:00 | 00:30 | 6.50 | 6.50 | 0.00 | 0.00 | 0.00
    """
    rows = AttendanceParserService.parse_rows_type_a(raw_text)
    assert len(rows) == 2
    assert rows[0].date == "02/10/2022"
    assert rows[1].date == "07/10/2022"


def test_parse_rows_type_b():
    raw_text = """
    1/9/22 | חמישי | 8:30 | 12:00 | 3.50 | ערב חג
    2/9/22 | שישי | 8:30 | 12:00 | 3.50 | 
    """
    rows = AttendanceParserService.parse_rows_type_b(raw_text)
    assert len(rows) == 2
    assert rows[0].date == "1/9/22"
    assert rows[0].notes == "ערב חג"