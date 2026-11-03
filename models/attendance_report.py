from abc import ABC
from dataclasses import dataclass, field
from typing import List, Any
from typing import List, Any, Optional


@dataclass(frozen=True)
class BaseAttendanceReport(ABC):
    """Abstract base class containing common report attributes (Immutable)."""
    report_type: str


@dataclass(frozen=True)
class AttendanceReportTypeA(BaseAttendanceReport):
    """Report attributes for Type A including rows list, summary data, and company name (Immutable)."""
    company_name: str
    rows: List[Any] = field(default_factory=list)
    summary: Optional[Any] = None


@dataclass(frozen=True)
class AttendanceReportTypeB(BaseAttendanceReport):
    """Report attributes for Type B including rows list, summary data, employee name, and report month (Immutable)."""
    employee_name: str
    report_month: str
    rows: List[Any] = field(default_factory=list)
    summary: Optional[Any] = None