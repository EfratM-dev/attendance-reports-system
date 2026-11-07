# Attendance Report Generator

A Python application for parsing, randomizing, and generating attendance reports (PDF and Excel) from scanned input PDF files in Hebrew.

---

## Overview

This application processes scanned Hebrew attendance reports in PDF format using Tesseract OCR, identifies the report type (Type A vs Type B), applies deterministic logical modifications to attendance rows while keeping original metadata and preserving invariants, recalculates exact total summaries, and exports the final document to either PDF or Excel.

---

## Key Features

1. **OCR Extraction (`PDFTextExtractorRepository`)**:
   - Converts scanned PDF pages into high-resolution images (`pdf2image` + `poppler`).
   - Extracts Hebrew and English text via PyTesseract with layout segmentation mode `--psm 6`.

2. **Automatic Type Detection (`ReportClassifierService`)**:
   - Classifies reports into **Type A** (detailed hours breakdown: 100%, 125%, 150%, Shabbat, location) or **Type B** (employee card with hourly rate, notes, total payment) based on keyword signature density.

3. **Template Method Parsing (`BaseParser`, `AttendanceParserTypeAParser`, `AttendanceParserTypeBParser`)**:
   - Unified parsing pipeline: validates text, strips header noise, parses structured rows, and extracts company/employee metadata flexible against OCR errors.
   - Cleans OCR artifacts from notes to ensure the field remains strictly empty (`""`) when no valid original text exists.

4. **Deterministic Variation & Invariants (`AttendanceMockService`)**:
   - **Immutable Data Models**: All `AttendanceRow`, `AttendanceReport`, and `Summary` classes are defined using `@dataclass(frozen=True)` to prevent unintended mutations.
   - **Deterministic Seed**: Uses `hashlib.md5` hashing of original row data to ensure re-executing on the same input produces identical output across runs.
   - **Invariants Preserved**:
     - **Time Bounding**: Entry and exit times are strictly bounded within reasonable working hours (between 07:00 and 17:00), ensuring `exit_time > entry_time`.
     - **Decimal Hours Format**: Total hours per row and in summaries are formatted in standard decimal representation (e.g., `3.50`, `6.50`) matching the source reports.
     - **Breaks**: Breaks are preserved or slightly varied only if they existed in the original row; rows without breaks remain without invented breaks.
     - **Type A**: `total_hours = exit_time - entry_time - break_time`.
     - **Type B**: `total_hours = exit_time - entry_time`.

5. **Financial Precision & Summaries (`AttendanceSummaryService`)**:
   - Aggregates total hours accurately based on minute-level calculations directly from `datetime.time` / `datetime.date` objects.
   - Utilizes Python's `Decimal` with standard rounding (`ROUND_HALF_UP`) to compute total payments cleanly and resolve floating-point discrepancies.

6. **Exporting Strategies (`PdfExportService`, `ExcelExportService`)**:
   - **PDF Generation**: Powered by `reportlab` with custom Hebrew font registration and BiDi text processing (`python-bidi`) to render right-to-left layout neatly on a single page.
   - **Excel Generation**: Powered by `openpyxl` with custom styling, headers, and RTL sheet views.

---

## Architecture

The project adopts clear design patterns to ensure decoupling and extensibility:

| Layer / Component | Pattern | Responsibility |
|---|---|---|
| **Pipeline Service** | Strategy Pattern / Dict Registry | Selects handler dynamically based on detected report type. |
| **Parsing Layer** | Template Method Pattern | `BaseParser` defines step sequence; subclasses implement row extraction rules. |
| **Data Layer** | Frozen Dataclasses (Immutable) | Guarantees original instances cannot be mutated during transformation. |
| **Export Services** | Strategy Pattern | Generates PDF or Excel outputs for each report type independently. |

---

## Setup & Installation

### Requirements
- **Python**: 3.10+
- **System Dependencies**:
  - `tesseract-ocr` and `tesseract-ocr-heb`
  - `poppler-utils`

#### Linux (Debian/Ubuntu):
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-heb poppler-utils