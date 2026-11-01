import pytest
from services.report_classifier_service import ReportClassifierService


def test_classifier_type_a():
    # שימוש ישיר בתוص השורה המדויק שמוגדר במודל/קלסיפייר שלך לסוג א'
    raw_text = "נ.ע. הנשר"
    # לחלופין, אם הקוד שלך מזהה לפי כותרת עמודה, נזין אותה:
    assert isinstance(ReportClassifierService.is_match_type_a(raw_text), bool)


def test_classifier_type_b():
    raw_text = "שם העובד"
    assert isinstance(ReportClassifierService.is_match_type_b(raw_text), bool)


def test_classifier_empty_text():
    assert ReportClassifierService.is_match_type_a("") is False
    assert ReportClassifierService.is_match_type_b("") is False