from abc import ABC
from dataclasses import dataclass


@dataclass
class BaseSummary(ABC):
    """מחלקה אבסטרקטית למאפייני הסיכום המשותפים."""
    work_days: str
    hours: str


@dataclass
class SummaryTypeA(BaseSummary):
    """מאפייני סיכום עבור סוג A[cite: 9]."""
    hours_100: str
    hours_125: str
    hours_150: str
    shabbat_150: str
    bonus: str
    travel: str


@dataclass
class SummaryTypeB(BaseSummary):
    """מאפייני סיכום עבור סוג B[cite: 9]."""
    hourly_rate: str
    total_payment: str