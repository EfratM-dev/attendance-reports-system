class ReportClassifierService:
    """שירות האחראי על בדיקת התאמת הדו"ח לסוג A או סוג B באמצעות ערכים בוליאניים."""

    @staticmethod
    def is_match_type_a(raw_text: str) -> bool:
        """
        מחזירה True אם הטקסט מכיל את המאפיינים הייחודיים לסוג A, אחרת False.
        """
        if not raw_text:
            return False

        unique_features = ["מקום", "הפסקה", "100%", "125%", "150%"]
        matches_count = sum(1 for feature in unique_features if feature in raw_text)
        return matches_count >= 3

    @staticmethod
    def is_match_type_b(raw_text: str) -> bool:
        """
        מחזירה True אם הטקסט מכיל את המאפיינים הייחודיים לסוג B, אחרת False.
        """
        if not raw_text:
            return False

        # שימוש במרכאות יחידות בחוץ כדי למנוע התנגשות עם הגרשיים בתוך המחרוזת (סה"כ)
        unique_features = ['הערות', 'כרטיס', 'עובד', 'שם העובד','כרטיס עובד','סה' ,'מחיר']
        matches_count = sum(1 for feature in unique_features if feature in raw_text)
        return matches_count >= 1