from abc import ABC
from dataclasses import dataclass, field
from typing import List


@dataclass
class BaseAttendanceReport(ABC):
    """מחלקה אבסטרקטית הכוללת את מאפייני הדו"ח המשותפים."""
    report_type: str


@dataclass
class AttendanceReportTypeA(BaseAttendanceReport):
    """מאפייני דו"ח עבור סוג A הכוללים רשימת שורות סוג A, נתוני סיכום A ושם החברה[cite: 10]."""
    company_name: str
    rows: List = field(default_factory=list)
    summary: object = None


@dataclass
class AttendanceReportTypeB(BaseAttendanceReport):
    """מאפייני דו"ח עבור סוג B הכוללים רשימת שורות סוג B, נתוני סיכום B, שם העובד וחודש הדו"ח[cite: 10]."""
    employee_name: str
    report_month: str
    rows: List = field(default_factory=list)
    summary: object = None