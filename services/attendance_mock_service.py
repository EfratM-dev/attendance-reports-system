import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Optional, Union
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB


class AttendanceMockService:
    """
    שירות המייצר נתונים דטרמיניסטיים, אמינים והגיוניים עבור שורות נוכחות.
    השירות מבטיח כי הרצה על אותו קובץ/סט שורות תפיק תמיד את אותה התוצאה בדיוק.
    """

    @classmethod
    def _create_deterministic_rng(
        cls,
        rows: List,
        custom_seed: Optional[Union[int, str]] = None
    ) -> random.Random:
        """
        יוצר מחולל אקראיות (RNG) דטרמיניסטי המבוסס על תוכן שורות הדו"ח או seed מותאם אישית.
        השימוש ב-hashlib.md5 מבטיח זהות מוחלטת בין הרצות שונות וגרסאות פייתון שונות.
        """
        if isinstance(custom_seed, int):
            return random.Random(custom_seed)
        if isinstance(custom_seed, str):
            seed_int = int(hashlib.md5(custom_seed.encode('utf-8')).hexdigest()[:8], 16)
            return random.Random(seed_int)

        # יצירת טביעת אצבע (Fingerprint) ייחודית וקבועה מהשורות המקוריות
        data_fingerprint = "|".join(
            f"{getattr(r, 'date', '')}_{getattr(r, 'day_of_week', '')}_{getattr(r, 'location', '')}_{getattr(r, 'notes', '')}_{i}"
            for i, r in enumerate(rows)
        )
        if not data_fingerprint.strip('|'):
            data_fingerprint = "default_attendance_deterministic_seed"

        seed_int = int(hashlib.md5(data_fingerprint.encode('utf-8')).hexdigest()[:8], 16)
        return random.Random(seed_int)

    @staticmethod
    def _generate_random_entry_time(rng: Optional[random.Random] = None) -> str:
        """יוצר שעת כניסה בין 07:00 ל-15:00 בצורה דטרמיניסטית לפי ה-RNG."""
        generator = rng if rng is not None else random
        hour = generator.randint(7, 15)
        minute = generator.choice([0, 15, 30, 45])
        if hour == 15:
            minute = 0
        return f'{hour:02d}:{minute:02d}'

    @staticmethod
    def _generate_random_exit_time(entry_str: str, rng: Optional[random.Random] = None) -> str:
        """יוצר שעת יציאה המאוחרת משעת הכניסה ועד לשעה 16:00 בצורה דטרמיניסטית."""
        generator = rng if rng is not None else random
        entry_dt = datetime.strptime(entry_str, '%H:%M')
        max_exit_dt = entry_dt.replace(hour=16, minute=0)

        min_exit_dt = entry_dt + timedelta(hours=1)
        if min_exit_dt > max_exit_dt:
            min_exit_dt = max_exit_dt

        possible_minutes = list(range(
            int((min_exit_dt - entry_dt).total_seconds() / 60),
            int((max_exit_dt - entry_dt).total_seconds() / 60) + 1,
            15
        ))
        if not possible_minutes:
            exit_dt = max_exit_dt
        else:
            delta_minutes = generator.choice(possible_minutes)
            exit_dt = entry_dt + timedelta(minutes=delta_minutes)

        return exit_dt.strftime('%H:%M')

    @staticmethod
    def _calculate_net_hours(entry_str: str, exit_str: str, break_str: str) -> float:
        """מחשב באופן מדויק את סך שעות העבודה בניכוי ההפסקה."""
        fmt = '%H:%M'
        entry = datetime.strptime(entry_str, fmt)
        exit_t = datetime.strptime(exit_str, fmt)
        break_t = datetime.strptime(break_str, fmt)

        total_minutes = (exit_t - entry).total_seconds() / 60
        break_minutes = (break_t.hour * 60) + break_t.minute

        net_minutes = max(0.0, total_minutes - break_minutes)
        return round(net_minutes / 60, 2)

    @classmethod
    def randomize_rows_type_a(
        cls,
        rows: List[AttendanceRowTypeA],
        seed: Optional[Union[int, str]] = None
    ) -> List[AttendanceRowTypeA]:
        """
        מעדכן שורות מסוג A בווריאציה הגיונית ודטרמיניסטית.
        הרצה חוזרת על אותו קובץ תמיד תניב נתונים זהים.
        משמרת במדויק את יום השבוע והמקום מקובץ המקור.
        """
        rng = cls._create_deterministic_rng(rows, seed)

        for row in rows:
            entry = cls._generate_random_entry_time(rng)
            exit_t = cls._generate_random_exit_time(entry, rng)
            break_minutes = rng.choice([15, 30, 45, 60])
            break_t = f'{break_minutes // 60:02d}:{break_minutes % 60:02d}'

            net_hours = cls._calculate_net_hours(entry, exit_t, break_t)

            # שימור יום השבוע מקובץ המקור
            original_day = getattr(row, 'day_of_week', '')
            if not original_day or original_day.strip() == '':
                row.day_of_week = "לא זוהה"
            else:
                row.day_of_week = original_day.strip()

            # שימור המקום מקובץ המקור
            original_loc = getattr(row, 'location', '')
            if not original_loc or original_loc.strip() == '':
                row.location = "לא זוהה"
            else:
                row.location = original_loc.strip()

            # חישוב שעות ואחוזים בהתאם ליום השבוע המקורי
            h_100 = 0.0
            h_125 = 0.0
            h_150 = 0.0
            shabbat_hours = 0.0

            if 'שבת' in row.day_of_week:
                shabbat_hours = net_hours
            else:
                if net_hours <= 8.0:
                    h_100 = net_hours
                else:
                    h_100 = 8.0
                    overtime = net_hours - 8.0
                    if overtime <= 2.0:
                        h_125 = overtime
                    else:
                        h_125 = 2.0
                        h_150 = overtime - 2.0

            row.entry_time = entry
            row.exit_time = exit_t
            row.break_time = break_t
            row.total_hours = f'{net_hours:.2f}'
            row.hours_100 = f'{h_100:.2f}' if h_100 > 0 else '0.00'
            row.hours_125 = f'{h_125:.2f}' if h_125 > 0 else '0.00'
            row.hours_150 = f'{h_150:.2f}' if h_150 > 0 else '0.00'
            row.shabbat = f'{shabbat_hours:.2f}' if shabbat_hours > 0 else '0.00'

            # וידוא תאריך תקין
            if not getattr(row, 'date', None) or not row.date.strip():
                row.date = "לא זוהה"

        return rows

    @classmethod
    def randomize_rows_type_b(
        cls,
        rows: List[AttendanceRowTypeB],
        seed: Optional[Union[int, str]] = None
    ) -> List[AttendanceRowTypeB]:
        """
        מעדכן שורות מסוג B בווריאציה הגיונית ודטרמיניסטית.
        הרצה חוזרת על אותו קובץ תמיד תניב נתונים זהים.
        משמרת במדויק את יום השבוע וההערות מקובץ המקור.
        """
        rng = cls._create_deterministic_rng(rows, seed)

        for row in rows:
            entry = cls._generate_random_entry_time(rng)
            exit_t = cls._generate_random_exit_time(entry, rng)
            break_minutes = rng.choice([15, 30, 45, 60])
            break_t = f'{break_minutes // 60:02d}:{break_minutes % 60:02d}'

            net_hours = cls._calculate_net_hours(entry, exit_t, break_t)

            # שימור יום השבוע מקובץ המקור
            original_day = getattr(row, 'day_of_week', '')
            if not original_day or original_day.strip() == '':
                row.day_of_week = "לא זוהה"
            else:
                row.day_of_week = original_day.strip()

            # שימור הערות
            original_notes = getattr(row, 'notes', '')
            row.notes = original_notes if original_notes else ""

            row.entry_time = entry
            row.exit_time = exit_t
            row.total_hours = f'{net_hours:.2f}'

            if not getattr(row, 'date', None) or not row.date.strip():
                row.date = "לא זוהה"

        return rows
