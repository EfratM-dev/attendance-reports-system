from abc import ABC, abstractmethod
import re
from datetime import datetime, date, time
from typing import List, Optional, Union
from models.attendance_row import AttendanceRowTypeA, AttendanceRowTypeB


class BaseParser(ABC):
    """
    Abstract base class implementing Template Method for parsing attendance reports.
    Main process is shared while row parsing and specific filtering are implemented in subclasses.
    """

    @staticmethod
    def _validate_raw_text(raw_text: str) -> bool:
        """Initial check for text validity extracted by OCR."""
        if not raw_text or not isinstance(raw_text, str):
            return False
        if len(raw_text.strip()) < 10:
            return False
        return True

    def parse(self, raw_text: str) -> List:
        """
        Template Method:
        Manages sequential workflow: cleanup, splitting, header skipping, and row processing.
        """
        if not self._validate_raw_text(raw_text):
            raise ValueError('הטקסט שחולץ אינו תקין או ריק.')

        lines = raw_text.splitlines()
        rows = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if self._is_header_line(line_str):
                continue

            row = self._parse_row(line_str)
            if row:
                rows.append(row)

        return rows

    @abstractmethod
    def _is_header_line(self, line_str: str) -> bool:
        """Identifies header lines to skip."""
        pass

    @abstractmethod
    def _parse_row(self, line_str: str):
        """Parses a specific row according to report structure."""
        pass

    @staticmethod
    def _parse_time(time_str: str, default_time: time) -> time:
        """Helper method to parse string into a datetime.time object safely."""
        if not time_str:
            return default_time
        try:
            cleaned = time_str.replace('.', ':').strip()
            parts = cleaned.split(':')
            if len(parts) == 2:
                h, m = int(parts[0]), int(parts[1])
                if 0 <= h < 24 and 0 <= m < 60:
                    return time(hour=h, minute=m)
        except (ValueError, IndexError):
            pass
        return default_time

    @staticmethod
    def _parse_and_validate_date(date_str: str) -> Union[date, str]:
        """Cleans and validates whether the given string represents a legitimate calendar date. Returns date object or fallback string."""
        if not date_str:
            return "לא זוהה"
        cleaned = re.sub(r'\s*[\/\.\-\|]\s*', '/', date_str.strip())
        parts = cleaned.split('/')
        if len(parts) != 3:
            return "לא זוהה"
        try:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            if year < 100:
                year += 2000

            if year > 2030 or year < 2000:
                return "לא זוהה"

            dt = datetime(year, month, day)
            return dt.date()
        except (ValueError, IndexError):
            return "לא זוהה"


class AttendanceParserTypeAParser(BaseParser):
    """Parser implementation for Type A report."""

    def _is_header_line(self, line_str: str) -> bool:
        if 'תאריך' in line_str and any(k in line_str for k in ['כניסה', 'יציאה', 'מקום', 'הפסקה', 'שבת']):
            return True
        if any(k in line_str for k in ['בע"מ', 'בע״מ', 'בעמ']) and not any(c.isdigit() for c in line_str):
            return True
        if sum(1 for c in line_str if c.isdigit()) < 3:
            return True
        return False

    def _parse_row(self, line_str: str):
        date_pattern = re.compile(r'(\b\d{1,2}\s*[\/\.\-\|]\s*\d{1,2}\s*[\/\.\-\|]\s*\d{2,4}\b)')
        time_pattern = re.compile(r'\b\d{1,2}[:\.]\d{2}\b')
        day_pattern = re.compile(r'(יום\s+(?:ראשון|שני|שלישי|רביעי|חמישי|שישי)|ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)')

        digits_count = sum(1 for c in line_str if c.isdigit())

        date_match = date_pattern.search(line_str)
        if date_match:
            raw_d = date_match.group(1)
            date_val = self._parse_and_validate_date(raw_d)
        else:
            times_check = time_pattern.findall(line_str)
            if not times_check and digits_count < 6:
                return None
            date_val = "לא זוהה"

        day_match = day_pattern.search(line_str)
        day_val = day_match.group(1).strip() if day_match else "לא זוהה"

        times = time_pattern.findall(line_str)
        entry_t = self._parse_time(times[0], time(8, 0)) if len(times) > 0 else time(8, 0)
        exit_t = self._parse_time(times[1], time(15, 0)) if len(times) > 1 else time(15, 0)
        break_t = self._parse_time(times[2], time(0, 30)) if len(times) > 2 else time(0, 30)

        today = datetime.today().date()
        entry_dt = datetime.combine(today, entry_t)
        exit_dt = datetime.combine(today, exit_t)
        if exit_dt < entry_dt:
            exit_dt = exit_dt.replace(day=exit_dt.day + 1)

        break_dt_obj = datetime.combine(today, break_t)
        total_minutes = max(0.0,
                            (exit_dt - entry_dt).total_seconds() / 60 - (break_dt_obj.hour * 60 + break_dt_obj.minute))
        net_hours = round(total_minutes / 60, 2)
        tot_h = f"{net_hours:.2f}"

        floats = re.findall(r'\b\d+(?:[\.,]\d{1,2})?\b', line_str)
        decimal_floats = [f.replace(',', '.') for f in floats if '.' in f or ',' in f]

        h_100 = decimal_floats[1] if len(decimal_floats) > 1 else "0.00"
        h_125 = decimal_floats[2] if len(decimal_floats) > 2 else "0.00"
        h_150 = decimal_floats[3] if len(decimal_floats) > 3 else "0.00"
        shabbat_val = decimal_floats[4] if len(decimal_floats) > 4 else "0.00"

        cleaned = line_str
        if date_match:
            cleaned = cleaned.replace(date_match.group(1), '')
        for t in times:
            cleaned = cleaned.replace(t, '')
        for f in decimal_floats:
            cleaned = cleaned.replace(f, '')
        if day_match:
            cleaned = cleaned.replace(day_match.group(1), '')

        hebrew_words = [w.strip() for w in re.findall(r'[\u0590-\u05fe]{2,}', cleaned) if w.strip()]
        ignore_keywords = {'שבת', 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'יום', 'סה"כ', 'סהכ', 'שעות',
                           'תאריך', 'כניסה', 'יציאה', 'הפסקה', 'מקום'}
        location_val = "לא זוהה"
        for w in hebrew_words:
            if w not in ignore_keywords:
                location_val = w
                break

        return AttendanceRowTypeA(
            date=date_val,
            day_of_week=day_val,
            location=location_val,
            entry_time=entry_t,
            exit_time=exit_t,
            break_time=break_t,
            total_hours=tot_h,
            hours_100=h_100,
            hours_125=h_125,
            hours_150=h_150,
            shabbat=shabbat_val
        )


class AttendanceParserTypeBParser(BaseParser):
    """Parser implementation for Type B report."""

    def _is_header_line(self, line_str: str) -> bool:
        if 'תאריך' in line_str and any(k in line_str for k in ['כניסה', 'יציאה', 'שעות', 'בשבוע']):
            return True
        if any(k in line_str for k in ['מחיר לשעה', 'כרטיס עובד', 'שם העובד']) and not any(
                c.isdigit() for c in line_str):
            return True
        if sum(1 for c in line_str if c.isdigit()) < 3:
            return True
        return False

    def _parse_row(self, line_str: str):
        date_pattern = re.compile(r'(\b\d{1,2}\s*[\/\.\-\|]\s*\d{1,2}\s*[\/\.\-\|]\s*\d{2,4}\b)')
        time_pattern = re.compile(r'\b\d{1,2}[:\.]\d{2}\b')
        day_pattern = re.compile(r'(יום\s+(?:ראשון|שני|שלישי|רביעי|חמישי|שישי)|ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)')

        digits_count = sum(1 for c in line_str if c.isdigit())

        date_match = date_pattern.search(line_str)
        if date_match:
            raw_d = date_match.group(1)
            date_val = self._parse_and_validate_date(raw_d)
        else:
            dates_check = time_pattern.findall(line_str)
            if not dates_check and digits_count < 5:
                return None
            date_val = "לא זוהה"

        day_match = day_pattern.search(line_str)
        day_val = day_match.group(1).strip() if day_match else "לא זוהה"

        times = time_pattern.findall(line_str)
        entry_t = self._parse_time(times[0], time(8, 30)) if len(times) > 0 else time(8, 30)
        exit_t = self._parse_time(times[1], time(12, 0)) if len(times) > 1 else time(12, 0)

        today = datetime.today().date()
        entry_dt = datetime.combine(today, entry_t)
        exit_dt = datetime.combine(today, exit_t)
        if exit_dt < entry_dt:
            exit_dt = exit_dt.replace(day=exit_dt.day + 1)

        total_minutes = max(0.0, (exit_dt - entry_dt).total_seconds() / 60)
        net_hours = round(total_minutes / 60, 2)
        tot_h = f"{net_hours:.2f}"

        cleaned = line_str
        if date_match:
            cleaned = cleaned.replace(date_match.group(1), '')
        for t in times:
            cleaned = cleaned.replace(t, '')
        if day_match:
            cleaned = cleaned.replace(day_match.group(1), '')

        cleaned = re.sub(r'\b\d+([\\.,]\d+)?\b', '', cleaned)

        ignore_keywords = {'שבת', 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'יום', 'שעות', 'תאריך', 'כניסה',
                           'יציאה'}

        words = [w.strip() for w in re.findall(r'[\u0590-\u05fe]{2,}', cleaned) if w.strip()]

        meaningful_words = [w for w in words if
                            w not in ignore_keywords and len(w) >= 3 and w not in {'שמ', 'רו', 'אש', 'הר', 'ואט'}]

        notes_val = " ".join(meaningful_words) if meaningful_words else ""

        return AttendanceRowTypeB(
            date=date_val,
            day_of_week=day_val,
            entry_time=entry_t,
            exit_time=exit_t,
            total_hours=tot_h,
            notes=notes_val
        )


class AttendanceParserService:
    """Wrapper class to maintain compatible caller interface across system."""

    @staticmethod
    def parse_rows_type_a(raw_text: str) -> List[AttendanceRowTypeA]:
        parser = AttendanceParserTypeAParser()
        return parser.parse(raw_text)

    @staticmethod
    def parse_rows_type_b(raw_text: str) -> List[AttendanceRowTypeB]:
        parser = AttendanceParserTypeBParser()
        return parser.parse(raw_text)