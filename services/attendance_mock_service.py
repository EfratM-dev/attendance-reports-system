import hashlib
import random
from datetime import datetime, timedelta
from typing import List, Optional, Union
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB


class AttendanceMockService:
    """
    Service generating deterministic, reliable, and logical data for attendance rows.
    Ensures running on the same file/row set produces identical results.
    """

    @classmethod
    def _create_deterministic_rng(
        cls,
        rows: List,
        custom_seed: Optional[Union[int, str]] = None
    ) -> random.Random:
        """
        Creates a deterministic Random Number Generator based on row content or a custom seed.
        Using hashlib.md5 guarantees exact consistency across runs and Python versions.
        """
        if isinstance(custom_seed, int):
            return random.Random(custom_seed)
        if isinstance(custom_seed, str):
            seed_int = int(hashlib.md5(custom_seed.encode('utf-8')).hexdigest()[:8], 16)
            return random.Random(seed_int)

        # Create unique fingerprint from original rows
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
        """Generates entry time between 07:00 and 15:00 deterministically."""
        generator = rng if rng is not None else random
        hour = generator.randint(7, 15)
        minute = generator.choice([0, 15, 30, 45])
        if hour == 15:
            minute = 0
        return f'{hour:02d}:{minute:02d}'

    @staticmethod
    def _generate_random_exit_time(entry_str: str, rng: Optional[random.Random] = None) -> str:
        """Generates exit time after entry time up to 16:00 deterministically."""
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
        """Calculates net working hours deducting break time."""
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
        Updates Type A rows deterministically by creating new immutable row instances.
        """
        rng = cls._create_deterministic_rng(rows, seed)
        updated_rows = []

        for row in rows:
            entry = cls._generate_random_entry_time(rng)
            exit_t = cls._generate_random_exit_time(entry, rng)
            break_minutes = rng.choice([15, 30, 45, 60])
            break_t = f'{break_minutes // 60:02d}:{break_minutes % 60:02d}'

            net_hours = cls._calculate_net_hours(entry, exit_t, break_t)

            # Preserve day of week from source
            original_day = getattr(row, 'day_of_week', '')
            day_val = original_day.strip() if original_day and original_day.strip() else "לא זוהה"

            # Preserve location from source
            original_loc = getattr(row, 'location', '')
            loc_val = original_loc.strip() if original_loc and original_loc.strip() else "לא זוהה"

            # Calculate overtime hours according to day of week
            h_100 = 0.0
            h_125 = 0.0
            h_150 = 0.0
            shabbat_hours = 0.0

            if 'שבת' in day_val:
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

            date_val = getattr(row, 'date', '')
            if not date_val or not date_val.strip():
                date_val = "לא זוהה"

            # Create a new immutable row instance
            new_row = AttendanceRowTypeA(
                date=date_val,
                day_of_week=day_val,
                location=loc_val,
                entry_time=entry,
                exit_time=exit_t,
                break_time=break_t,
                total_hours=f'{net_hours:.2f}',
                hours_100=f'{h_100:.2f}' if h_100 > 0 else '0.00',
                hours_125=f'{h_125:.2f}' if h_125 > 0 else '0.00',
                hours_150=f'{h_150:.2f}' if h_150 > 0 else '0.00',
                shabbat=f'{shabbat_hours:.2f}' if shabbat_hours > 0 else '0.00'
            )
            updated_rows.append(new_row)

        return updated_rows


    @classmethod
    def randomize_rows_type_b(
            cls,
            rows: List[AttendanceRowTypeB],
            seed: Optional[Union[int, str]] = None
    ) -> List[AttendanceRowTypeB]:
        """
        Updates Type B rows deterministically by creating new immutable row instances.
        """
        rng = cls._create_deterministic_rng(rows, seed)
        updated_rows = []

        for row in rows:
            entry = cls._generate_random_entry_time(rng)
            exit_t = cls._generate_random_exit_time(entry, rng)
            break_minutes = rng.choice([15, 30, 45, 60])
            break_t = f'{break_minutes // 60:02d}:{break_minutes % 60:02d}'

            net_hours = cls._calculate_net_hours(entry, exit_t, break_t)

            # Preserve day of week from source
            original_day = getattr(row, 'day_of_week', '')
            day_val = original_day.strip() if original_day and original_day.strip() else "לא זוהה"

            # Preserve notes from source
            original_notes = getattr(row, 'notes', '')
            notes_val = original_notes if original_notes else ""

            date_val = getattr(row, 'date', '')
            if not date_val or not date_val.strip():
                date_val = "לא זוהה"

            # Create a new immutable row instance
            new_row = AttendanceRowTypeB(
                date=date_val,
                day_of_week=day_val,
                entry_time=entry,
                exit_time=exit_t,
                total_hours=f'{net_hours:.2f}',
                notes=notes_val
            )
            updated_rows.append(new_row)

        return updated_rows