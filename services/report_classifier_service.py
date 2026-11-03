class ReportClassifierService:
    """Service responsible for determining whether raw OCR text matches Type A or Type B report structure."""

    @staticmethod
    def is_match_type_a(raw_text: str) -> bool:
        """Returns True if text contains unique features of Type A report."""
        if not raw_text:
            return False

        unique_features = ["מקום", "הפסקה", "100%", "125%", "150%"]
        matches_count = sum(1 for feature in unique_features if feature in raw_text)
        return matches_count >= 3

    @staticmethod
    def is_match_type_b(raw_text: str) -> bool:
        """Returns True if text contains unique features of Type B report."""
        if not raw_text:
            return False

        unique_features = ['הערות', 'כרטיס', 'עובד', 'שם העובד', 'כרטיס עובד', 'סה"כ', 'מחיר']
        matches_count = sum(1 for feature in unique_features if feature in raw_text)
        return matches_count >= 1