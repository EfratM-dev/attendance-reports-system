from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class BaseSummary(ABC):
    """Abstract base class for common summary attributes (Immutable)."""
    work_days: str
    hours: str


@dataclass(frozen=True)
class SummaryTypeA(BaseSummary):
    """Summary attributes for Type A report (Immutable)."""
    hours_100: str
    hours_125: str
    hours_150: str
    shabbat_150: str
    bonus: str
    travel: str


@dataclass(frozen=True)
class SummaryTypeB(BaseSummary):
    """Summary attributes for Type B report (Immutable)."""
    hourly_rate: str
    total_payment: str