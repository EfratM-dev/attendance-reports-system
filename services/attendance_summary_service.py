from __future__ import annotations
from typing import List
from decimal import Decimal, ROUND_HALF_UP
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB
from models.summary import SummaryTypeA, SummaryTypeB


class AttendanceSummaryService:
    """Service calculating and creating summary objects based on updated attendance rows."""

    @staticmethod
    def calculate_summary_type_a(rows: List[AttendanceRowTypeA]) -> SummaryTypeA:
        total_days = len(rows)

        total_minutes = sum(
            int(round(float(row.total_hours) * 60))
            for row in rows
            if getattr(row, 'total_hours', None) and str(row.total_hours).replace('.', '', 1).isdigit()
        )
        total_100 = sum(
            int(round(float(row.hours_100) * 60))
            for row in rows
            if getattr(row, 'hours_100', None) and str(row.hours_100).replace('.', '', 1).isdigit()
        )
        total_125 = sum(
            int(round(float(row.hours_125) * 60))
            for row in rows
            if getattr(row, 'hours_125', None) and str(row.hours_125).replace('.', '', 1).isdigit()
        )
        total_150 = sum(
            int(round(float(row.hours_150) * 60))
            for row in rows
            if getattr(row, 'hours_150', None) and str(row.hours_150).replace('.', '', 1).isdigit()
        )
        total_shabbat = sum(
            int(round(float(row.shabbat) * 60))
            for row in rows
            if getattr(row, 'shabbat', None) and str(row.shabbat).replace('.', '', 1).isdigit()
        )

        total_bonus = sum(float(row.bonus) for row in rows if hasattr(row, 'bonus') and row.bonus)
        total_travel = sum(float(row.travel) for row in rows if hasattr(row, 'travel') and row.travel)

        return SummaryTypeA(
            work_days=str(total_days),
            hours=f"{total_minutes / 60:.2f}",
            hours_100=f"{total_100 / 60:.2f}",
            hours_125=f"{total_125 / 60:.2f}",
            hours_150=f"{total_150 / 60:.2f}",
            shabbat_150=f"{total_shabbat / 60:.2f}",
            bonus=str(round(total_bonus, 2)),
            travel=str(round(total_travel, 2))
        )

    @staticmethod
    def calculate_summary_type_b(rows: List[AttendanceRowTypeB]) -> SummaryTypeB:
        """Calculates total work days, total hours (in decimal format like 84.00), and payment summary for Type B report."""
        total_days = len(rows)
        total_minutes = 0

        for row in rows:
            if hasattr(row, 'entry_time') and hasattr(row, 'exit_time'):
                if hasattr(row.entry_time, 'hour') and hasattr(row.exit_time, 'hour'):
                    entry_mins = row.entry_time.hour * 60 + row.entry_time.minute
                    exit_mins = row.exit_time.hour * 60 + row.exit_time.minute
                    diff = exit_mins - entry_mins
                    if diff < 0:
                        diff += 24 * 60
                    total_minutes += max(0, diff)
                elif getattr(row, 'total_hours', None):
                    try:
                        total_minutes += int(round(float(row.total_hours) * 60))
                    except ValueError:
                        pass

        decimal_hours = total_minutes / 60.0
        hourly_rate_val = 30.65

        total_payment_dec = (Decimal(str(decimal_hours)) * Decimal(str(hourly_rate_val))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        total_payment = float(total_payment_dec)

        return SummaryTypeB(
            work_days=str(total_days),
            hours=f"{decimal_hours:.2f}",
            hourly_rate=f"{hourly_rate_val:.2f}",
            total_payment=f"{total_payment:,.2f}"
        )