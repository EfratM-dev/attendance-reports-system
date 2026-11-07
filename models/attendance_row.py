from abc import ABC
from dataclasses import dataclass
from typing import Optional, Union
from datetime import date, time, timedelta


@dataclass(frozen=True)
class BaseAttendanceRow(ABC):
    """Abstract base class for common attendance row attributes (Immutable)."""
    date: Union[str, date]
    day_of_week: str
    entry_time: Union[str, time]
    exit_time: Union[str, time]
    total_hours: Union[str, float, timedelta]


@dataclass(frozen=True)
class AttendanceRowTypeA(BaseAttendanceRow):
    """Row attributes for Type A report (Immutable)."""
    location: str
    break_time: Union[str, time]
    hours_100: Union[str, float]
    hours_125: Union[str, float]
    hours_150: Union[str, float]
    shabbat: Union[str, float]


@dataclass(frozen=True)
class AttendanceRowTypeB(BaseAttendanceRow):
    """Row attributes for Type B report (Immutable)."""
    notes: Optional[str] = ""