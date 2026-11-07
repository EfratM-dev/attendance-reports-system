import re
from datetime import date


class AttendanceMetadataService:
    """Service responsible for extracting report metadata reliably and flexibly against OCR errors."""

    _INVALID_NAMES = {'לא', 'זוהה', 'לא זוהה'}
    _HEBREW_MONTHS = {
        'ינו': '01', 'ינואר': '01', 'פבר': '02', 'פברואר': '02',
        'מרץ': '03', 'אפר': '04', 'אפריל': '04', 'מאי': '05',
        'יונ': '06', 'יוני': '06', 'יול': '07', 'יולי': '07',
        'אוג': '08', 'אוגוסט': '08', 'ספט': '09', 'ספטמבר': '09',
        'אוק': '10', 'אוקטובר': '10', 'נוב': '11', 'נובמבר': '11',
        'דצמ': '12', 'דצמבר': '12'
    }

    @staticmethod
    def extract_company_name(raw_text: str) -> str:
        """Extracts company name from Type A raw text."""
        lines = raw_text.splitlines()
        company_name = "לא זוהה"

        company_indicators = ['בע"מ', 'בע״מ', 'בעמ', 'כח אדם', 'חברה', 'שם המעסיק']
        for line in lines:
            line_str = line.strip()
            if any(term in line_str for term in company_indicators):
                clean_line = re.sub(r'דו"ח\s*נוכחות', '', line_str)
                clean_line = clean_line.replace('-', '').strip()
                if clean_line:
                    company_name = clean_line
                    break

        return company_name

    @classmethod
    def extract_employee_name(cls, raw_text: str) -> str:
        """Extracts employee name using regex flexible to whitespace and special characters."""
        match = re.search(r'שם\s*העובד\s*[:\-]?\s*([^\r\n]+)', raw_text)
        if match:
            raw_name = match.group(1)
            cleaned = re.sub(r'[\-_:.\\[\]|]', '', raw_name).strip()
            if cleaned and cleaned not in cls._INVALID_NAMES:
                return cleaned

        lines = raw_text.splitlines()
        for line in lines:
            if 'עובד' in line:
                parts = re.split(r'[:\-]', line)
                if len(parts) > 1:
                    cleaned = re.sub(r'[\-_:.\\[\]|]', '', parts[-1]).strip()
                    if cleaned and cleaned not in cls._INVALID_NAMES:
                        return cleaned

        return "לא זוהה"

    @classmethod
    def extract_report_month(cls, rows: list, raw_text: str, randomized_month_str: str) -> str:
        """Extracts report month using multiple fallback mechanisms."""
        if rows:
            for row in rows:
                d = getattr(row, 'date', '')
                if isinstance(d, date):
                    return f"{d.month:02d}/{d.year}"

                d_str = str(d)
                if d_str and ('/' in d_str or '.' in d_str):
                    d_parts = re.split(r'[\/\.]', d_str)
                    if len(d_parts) >= 2 and d_parts[1].isdigit():
                        m_num = f"{int(d_parts[1]):02d}"
                        y_num = d_parts[2] if len(d_parts) > 2 else ""
                        if len(y_num) == 2 and y_num.isdigit():
                            y_num = f"20{y_num}"
                        if len(m_num) == 2 and int(m_num) <= 12:
                            return f"{m_num}/{y_num}" if y_num else m_num

        month_match = re.search(r'\b(0?[1-9]|1[0-2])[\/\.](20\d{2}|\d{2})\b', raw_text)
        if month_match:
            m_num = f"{int(month_match.group(1)):02d}"
            y_num = month_match.group(2)
            if len(y_num) == 2:
                y_num = f"20{y_num}"
            return f"{m_num}/{y_num}"

        for h_name, m_code in cls._HEBREW_MONTHS.items():
            m_regex = re.search(rf'{h_name}[-\s/]?(\d{{2,4}})', raw_text)
            if m_regex:
                y_val = m_regex.group(1)
                if len(y_val) == 2:
                    y_val = f"20{y_val}"
                return f"{m_code}/{y_val}"

        if randomized_month_str and any(
                c.isdigit() for c in randomized_month_str) and randomized_month_str not in cls._INVALID_NAMES:
            return randomized_month_str

        return "09/2022"