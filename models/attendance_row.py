from abc import ABC
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BaseAttendanceRow(ABC):
    """מחלקה אבסטרקטית למאפייני השורה המשותפים."""
    date: str
    day_of_week: str
    entry_time: str
    exit_time: str
    total_hours: str


@dataclass
class AttendanceRowTypeA(BaseAttendanceRow):
    """מאפייני שורה עבור סוג A[cite: 7]."""
    location: str
    break_time: str
    hours_100: str
    hours_125: str
    hours_150: str
    shabbat: str


@dataclass
class AttendanceRowTypeB(BaseAttendanceRow):
    """מאפייני שורה עבור סוג B[cite: 7]."""
    notes: Optional[str] = ""