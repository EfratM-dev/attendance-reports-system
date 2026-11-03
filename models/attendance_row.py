from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BaseAttendanceRow(ABC):
    """Abstract base class for common attendance row attributes (Immutable)."""
    date: str
    day_of_week: str
    entry_time: str
    exit_time: str
    total_hours: str


@dataclass(frozen=True)
class AttendanceRowTypeA(BaseAttendanceRow):
    """Row attributes for Type A report (Immutable)."""
    location: str
    break_time: str
    hours_100: str
    hours_125: str
    hours_150: str
    shabbat: str


@dataclass(frozen=True)
class AttendanceRowTypeB(BaseAttendanceRow):
    """Row attributes for Type B report (Immutable)."""
    notes: Optional[str] = ""