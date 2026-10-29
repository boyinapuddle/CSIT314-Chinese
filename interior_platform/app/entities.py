from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class UserProfile:
    profile_id: Optional[int]
    name: str
    description: str
    status: str = "Active"

@dataclass
class UserAccount:
    account_id: Optional[int]
    username: str
    password_hash: str
    profile_id: int
    display_name: str
    email: str
    status: str = "Active"

@dataclass
class UserSession:
    session_id: Optional[int]
    account_id: int
    role: str
    created_at: str
    active: bool = True

@dataclass
class Company:
    company_id: Optional[int]
    designer_id: int
    name: str
    description: str
    phone: str
    email: str
    website: str
    address: str

@dataclass
class IDP:
    project_id: Optional[int]
    designer_id: int
    category_id: int
    title: str
    description: str
    project_status: str
    progress: int
    image_url: str = ""
    visible: bool = True
    updated_at: str = ""

@dataclass
class Favourite:
    favourite_id: Optional[int]
    customer_id: int
    project_id: int
    saved_at: str

@dataclass
class IDPCategory:
    category_id: Optional[int]
    name: str
    description: str
    status: str = "Active"

@dataclass
class ActivityEvent:
    event_id: Optional[int]
    event_type: str
    account_id: Optional[int]
    project_id: Optional[int]
    created_at: str

@dataclass
class ViewMetric:
    project_id: int
    views: int

@dataclass
class ShortlistMetric:
    project_id: int
    shortlists: int

@dataclass
class ReportSummary:
    period_label: str
    users: int
    projects: int
    views: int
    shortlists: int

@dataclass
class DailyReport(ReportSummary):
    pass

@dataclass
class WeeklyReport(ReportSummary):
    pass

@dataclass
class MonthlyReport(ReportSummary):
    pass
