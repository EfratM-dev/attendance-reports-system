from __future__ import annotations
from typing import List
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB
from models.summary import SummaryTypeA, SummaryTypeB


class AttendanceSummaryService:
    """שירות המחשב ומעודכן את טבלת הסיכום (Summary) על בסיס רשימת השורות המעודכנות."""

    @staticmethod
    def calculate_summary_type_a(rows: List[AttendanceRowTypeA]) -> SummaryTypeA:
        """
        מחשב את סיכום השעות והנתונים עבור דו"ח מסוג A מתוך רשימת השורות.
        """
        total_days = len(rows)
        total_hours = sum(float(row.total_hours) for row in rows if getattr(row, 'total_hours', None) and row.total_hours.replace('.', '', 1).isdigit())

        total_100 = sum(float(row.hours_100) for row in rows if getattr(row, 'hours_100', None) and row.hours_100.replace('.', '', 1).isdigit())
        total_125 = sum(float(row.hours_125) for row in rows if getattr(row, 'hours_125', None) and row.hours_125.replace('.', '', 1).isdigit())
        total_150 = sum(float(row.hours_150) for row in rows if getattr(row, 'hours_150', None) and row.hours_150.replace('.', '', 1).isdigit())

        total_shabbat = sum(float(row.shabbat) for row in rows if getattr(row, 'shabbat', None) and row.shabbat.replace('.', '', 1).isdigit())

        total_bonus = sum(float(row.bonus) for row in rows if hasattr(row, 'bonus') and row.bonus)
        total_travel = sum(float(row.travel) for row in rows if hasattr(row, 'travel') and row.travel)

        return SummaryTypeA(
            work_days=str(total_days),
            hours=str(round(total_hours, 2)),
            hours_100=str(round(total_100, 2)),
            hours_125=str(round(total_125, 2)),
            hours_150=str(round(total_150, 2)),
            shabbat_150=str(round(total_shabbat, 2)),
            bonus=str(round(total_bonus, 2)),
            travel=str(round(total_travel, 2))
        )

    @staticmethod
    def calculate_summary_type_b(rows: List[AttendanceRowTypeB]) -> SummaryTypeB:
        """
        מחשב את סיכום ימי העבודה והשעות עבור דו"ח מסוג B מתוך רשימת השורות.
        """
        total_days = len(rows)
        total_hours = sum(float(row.total_hours) for row in rows if getattr(row, 'total_hours', None) and row.total_hours.replace('.', '', 1).isdigit())

        # תעריף שעה לדוגמה כפי שמופיע בקובץ המקור
        hourly_rate_val = 30.65
        total_payment = round(total_hours * hourly_rate_val, 2)

        return SummaryTypeB(
            work_days=str(total_days),
            hours=str(round(total_hours, 2)),
            hourly_rate=f"{hourly_rate_val:.2f}",
            total_payment=f"{total_payment:,.2f}"
        )