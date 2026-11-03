from abc import ABC, abstractmethod
import re
from datetime import datetime
from typing import List, Optional
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
    def _parse_and_validate_date(date_str: str) -> str:
        """Cleans and validates whether the given string represents a legitimate calendar date."""
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

            datetime(year, month, day)
            return f"{day}/{month}/{year}"
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
        times = [t.replace('.', ':') for t in times]
        entry_t = times[0] if len(times) > 0 else "08:00"
        exit_t = times[1] if len(times) > 1 else "15:00"
        break_t = times[2] if len(times) > 2 else "00:30"

        floats = re.findall(r'\b\d+(?:[\.,]\d{1,2})?\b', line_str)
        decimal_floats = [f.replace(',', '.') for f in floats if '.' in f or ',' in f]

        tot_h = decimal_floats[0] if len(decimal_floats) > 0 else "6.50"
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
            times_check = time_pattern.findall(line_str)
            if not times_check and digits_count < 5:
                return None
            date_val = "לא זוהה"

        day_match = day_pattern.search(line_str)
        day_val = day_match.group(1).strip() if day_match else "לא זוהה"

        times = time_pattern.findall(line_str)
        times = [t.replace('.', ':') for t in times]
        entry_t = times[0] if len(times) > 0 else "08:30"
        exit_t = times[1] if len(times) > 1 else "12:00"

        floats = re.findall(r'\b\d+(?:[\\.,]\d{1,2})?\b', line_str)
        decimal_floats = [f.replace(',', '.') for f in floats if '.' in f or ',' in f]
        tot_h = decimal_floats[0] if len(decimal_floats) > 0 else "3.50"

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
        ignore_keywords = {'שבת', 'ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'יום', 'שעות', 'תאריך', 'כניסה',
                           'יציאה'}
        notes_words = [w for w in hebrew_words if w not in ignore_keywords]
        notes_val = " ".join(notes_words) if notes_words else ""

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