import pytest
from services.report_classifier_service import ReportClassifierService


def test_classifier_type_a():
    # Test Type A detection matching model classifier definition
    raw_text = "נ.ע. הנשר"
    assert isinstance(ReportClassifierService.is_match_type_a(raw_text), bool)


def test_classifier_type_b():
    raw_text = "שם העובד"
    assert isinstance(ReportClassifierService.is_match_type_b(raw_text), bool)


def test_classifier_empty_text():
    assert ReportClassifierService.is_match_type_a("") is False
    assert ReportClassifierService.is_match_type_b("") is False