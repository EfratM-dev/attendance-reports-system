import hashlib
import random
from datetime import datetime, timedelta, time, date
from typing import List, Optional, Union
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB


class AttendanceMockService:
    """
    Service generating deterministic, reliable, and logical data for attendance rows.
    Ensures running on the same file/row set produces identical results.
    """

    EARLIEST_ENTRY_HOUR = 7
    LATEST_EXIT_HOUR = 17

    ENTRY_OFFSET_MIN = -30
    ENTRY_OFFSET_MAX = 30
    EXIT_OFFSET_MIN = -30
    EXIT_OFFSET_MAX = 30

    BREAK_DEVIATION_RANGE = 15
    MIN_ALLOWED_BREAK = 10
    MAX_ALLOWED_BREAK = 90

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

        data_fingerprint = "|".join(
            f"{getattr(r, 'date', '')}_{getattr(r, 'day_of_week', '')}_{getattr(r, 'location', '')}_{getattr(r, 'notes', '')}_{i}"
            for i, r in enumerate(rows)
        )
        if not data_fingerprint.strip('|'):
            data_fingerprint = "default_attendance_deterministic_seed"

        seed_int = int(hashlib.md5(data_fingerprint.encode('utf-8')).hexdigest()[:8], 16)
        return random.Random(seed_int)

    @classmethod
    def _generate_random_entry_time(cls, original_entry: Optional[time] = None,
                                    rng: Optional[random.Random] = None) -> time:
        """Generates realistic entry time bounded strictly between 07:00 and the afternoon."""
        generator = rng if rng is not None else random
        today = datetime.today().date()

        if original_entry and isinstance(original_entry, time):
            dt = datetime.combine(today, original_entry)
            if not (cls.EARLIEST_ENTRY_HOUR <= dt.hour < 12):
                hour = generator.randint(cls.EARLIEST_ENTRY_HOUR, 10)
                minute = generator.randint(0, 59)
                return time(hour=hour, minute=minute)

            offset_minutes = generator.randint(cls.ENTRY_OFFSET_MIN, cls.ENTRY_OFFSET_MAX)
            dt += timedelta(minutes=offset_minutes)

            final_hour = max(cls.EARLIEST_ENTRY_HOUR, min(11, dt.hour))
            return time(hour=final_hour, minute=dt.minute)
        else:
            hour = generator.randint(cls.EARLIEST_ENTRY_HOUR, 10)
            minute = generator.randint(0, 59)
            return time(hour=hour, minute=minute)

    @classmethod
    def _generate_random_exit_time(cls, entry_t: time, original_entry: Optional[time] = None,
                                   original_exit: Optional[time] = None, rng: Optional[random.Random] = None) -> time:
        """Generates realistic exit time ensuring it is after entry and strictly up to 17:00."""
        generator = rng if rng is not None else random
        today = datetime.today().date()
        entry_dt = datetime.combine(today, entry_t)

        max_allowed_exit_dt = datetime.combine(today, time(cls.LATEST_EXIT_HOUR, 0))

        if original_exit and isinstance(original_exit, time) and original_entry and isinstance(original_entry, time):
            orig_exit_dt = datetime.combine(today, original_exit)
            if orig_exit_dt <= max_allowed_exit_dt and orig_exit_dt > entry_dt:
                offset_minutes = generator.randint(cls.EXIT_OFFSET_MIN, cls.EXIT_OFFSET_MAX)
                exit_dt = orig_exit_dt + timedelta(minutes=offset_minutes)
                if exit_dt > entry_dt and exit_dt <= max_allowed_exit_dt:
                    return exit_dt.time()

        min_exit_dt = entry_dt + timedelta(hours=6)
        max_possible_exit = min(max_allowed_exit_dt, entry_dt + timedelta(hours=9.5))

        if min_exit_dt >= max_possible_exit:
            exit_dt = max_allowed_exit_dt
        else:
            delta_mins = generator.randint(360, int((max_possible_exit - entry_dt).total_seconds() / 60))
            exit_dt = entry_dt + timedelta(minutes=delta_mins)

        return exit_dt.time()

    @staticmethod
    def _calculate_net_hours_type_a(entry_t: time, exit_t: time, break_t: Optional[time]) -> float:
        """Calculates net working hours for Type A as a precise decimal float."""
        today = datetime.today().date()
        entry_dt = datetime.combine(today, entry_t)
        exit_dt = datetime.combine(today, exit_t)
        if exit_dt < entry_dt:
            exit_dt = exit_dt.replace(day=exit_dt.day + 1)

        break_minutes = 0
        if break_t and isinstance(break_t, time):
            break_minutes = (break_t.hour * 60) + break_t.minute

        total_minutes = (exit_dt - entry_dt).total_seconds() / 60
        net_minutes = max(0.0, total_minutes - break_minutes)
        return round(net_minutes / 60, 2)

    @staticmethod
    def _calculate_net_hours_type_b_decimal(entry_t: time, exit_t: time) -> float:
        """Calculates net working hours for Type B as a precise decimal float (e.g. 8.50)."""
        today = datetime.today().date()
        entry_dt = datetime.combine(today, entry_t)
        exit_dt = datetime.combine(today, exit_t)
        if exit_dt < entry_dt:
            exit_dt = exit_dt.replace(day=exit_dt.day + 1)

        total_minutes = (exit_dt - entry_dt).total_seconds() / 60
        net_minutes = max(0.0, total_minutes)
        return round(net_minutes / 60, 2)

    @classmethod
    def randomize_rows_type_a(
            cls,
            rows: List[AttendanceRowTypeA],
            seed: Optional[Union[int, str]] = None
    ) -> List[AttendanceRowTypeA]:
        rng = cls._create_deterministic_rng(rows, seed)
        updated_rows = []

        for row in rows:
            orig_entry = getattr(row, 'entry_time', None)
            orig_exit = getattr(row, 'exit_time', None)
            orig_break = getattr(row, 'break_time', None)

            entry = cls._generate_random_entry_time(orig_entry, rng)
            exit_t = cls._generate_random_exit_time(entry, orig_entry, orig_exit, rng)

            break_t = None
            if orig_break and isinstance(orig_break, time):
                break_mins = orig_break.hour * 60 + orig_break.minute
                offset_break = rng.randint(-cls.BREAK_DEVIATION_RANGE, cls.BREAK_DEVIATION_RANGE)
                break_mins = max(cls.MIN_ALLOWED_BREAK, min(cls.MAX_ALLOWED_BREAK, break_mins + offset_break))
                break_t = time(hour=break_mins // 60, minute=break_mins % 60)

            net_hours = cls._calculate_net_hours_type_a(entry, exit_t, break_t)

            original_day = getattr(row, 'day_of_week', '')
            day_val = original_day.strip() if original_day and original_day.strip() else "לא זוהה"

            original_loc = getattr(row, 'location', '')
            loc_val = original_loc.strip() if original_loc and original_loc.strip() else "לא זוהה"

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

            date_val = getattr(row, 'date', 'לא זוהה')

            new_row = AttendanceRowTypeA(
                date=date_val,
                day_of_week=day_val,
                location=loc_val,
                entry_time=entry,
                exit_time=exit_t,
                break_time=break_t if break_t else "00:00",
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
        rng = cls._create_deterministic_rng(rows, seed)
        updated_rows = []

        for row in rows:
            orig_entry = getattr(row, 'entry_time', None)
            orig_exit = getattr(row, 'exit_time', None)

            entry = cls._generate_random_entry_time(orig_entry, rng)
            exit_t = cls._generate_random_exit_time(entry, orig_entry, orig_exit, rng)

            net_hours = cls._calculate_net_hours_type_b_decimal(entry, exit_t)

            original_day = getattr(row, 'day_of_week', '')
            day_val = original_day.strip() if original_day and original_day.strip() else "לא זוהה"

            original_notes = getattr(row, 'notes', '')
            notes_val = original_notes if original_notes else ""

            date_val = getattr(row, 'date', 'לא זוהה')

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