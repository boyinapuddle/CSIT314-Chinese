from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash


@dataclass
class UserProfile:
    profile_id: Optional[int]
    name: str
    description: str
    role: str
    status: str = "Active"

    @classmethod
    def get_profile(cls, profile_id):
        from .repositories import ProfileRepository
        return ProfileRepository().get(profile_id)

    @classmethod
    def search_profiles(cls, keyword=""):
        from .repositories import ProfileRepository
        return ProfileRepository().search(keyword)

    @classmethod
    def create_profile(cls, name, description="", role="Customer"):
        from .repositories import ProfileRepository
        repository = ProfileRepository()
        name = " ".join(name.split())
        allowed_roles = {"User Admin", "Interior Designer", "Customer", "Platform Manager"}
        if not name:
            raise ValueError("Profile name is required.")
        if role not in allowed_roles:
            raise ValueError("Invalid profile role.")
        if repository.find_by_name(name):
            raise ValueError("A profile with this name already exists.")
        return repository.create(name, description.strip(), role)

    @classmethod
    def update_profile(cls, profile_id, name, description="", role="Customer"):
        from .repositories import AccountRepository, ProfileRepository
        repository = ProfileRepository()
        current = repository.get(profile_id)
        name = name.strip()
        allowed_roles = {"User Admin", "Interior Designer", "Customer", "Platform Manager"}
        if not current:
            raise ValueError("Profile not found.")
        if not name:
            raise ValueError("Profile name is required.")
        if role not in allowed_roles:
            raise ValueError("Invalid profile role.")
        if repository.find_by_name(name, profile_id):
            raise ValueError("A profile with this name already exists.")
        if current["role"] == "User Admin" and role != "User Admin" and current["status"] == "Active":
            if AccountRepository().active_admin_count(exclude_profile_id=profile_id) == 0:
                raise ValueError("This role cannot be changed because it would leave no active User Admin account.")
        return repository.update(profile_id, name, description.strip(), role)

    @classmethod
    def suspend_profile(cls, profile_id):
        from .repositories import AccountRepository, ProfileRepository
        profile = ProfileRepository().get(profile_id)
        if not profile:
            raise ValueError("Profile not found.")
        if profile["role"] == "User Admin" and profile["status"] == "Active":
            if AccountRepository().active_admin_count(exclude_profile_id=profile_id) == 0:
                raise ValueError("This profile cannot be suspended because it would leave no active User Admin account.")
        return ProfileRepository().suspend(profile_id)

    @classmethod
    def reactivate_profile(cls, profile_id):
        from .repositories import ProfileRepository
        return ProfileRepository().reactivate(profile_id)

    @classmethod
    def delete_profile(cls, profile_id):
        from .repositories import ProfileRepository
        repository = ProfileRepository()
        profile = repository.get(profile_id)
        if not profile:
            raise ValueError("Profile not found.")
        if repository.account_count(profile_id) > 0:
            raise ValueError("This profile is assigned to one or more user accounts. Reassign those accounts before deleting it.")
        return repository.delete(profile_id)


@dataclass
class UserAccount:
    account_id: Optional[int]
    username: str
    password_hash: str
    profile_id: int
    display_name: str
    email: str
    status: str = "Active"

    @classmethod
    def get_account(cls, account_id):
        from .repositories import AccountRepository
        return AccountRepository().get(account_id)

    @classmethod
    def search_accounts(cls, keyword=""):
        from .repositories import AccountRepository
        return AccountRepository().search(keyword)

    @classmethod
    def create_account(cls, username, password, profile_id, display_name, email):
        from .repositories import AccountRepository, ProfileRepository
        profile = ProfileRepository().get(profile_id)
        if not profile or profile["status"] != "Active":
            raise ValueError("An active profile is required to create an account.")
        password_hash = generate_password_hash(password)
        return AccountRepository().create(
            username.strip(),
            password_hash,
            profile_id,
            display_name.strip(),
            email.strip(),
        )

    @classmethod
    def update_account(cls, account_id, display_name, email, profile_id):
        from .repositories import AccountRepository, ProfileRepository
        repository = AccountRepository()
        account = repository.get(account_id)
        target_profile = ProfileRepository().get(profile_id)
        if not account:
            raise ValueError("Account not found.")
        if not target_profile:
            raise ValueError("Profile not found.")
        if account["role"] == "User Admin" and target_profile["role"] != "User Admin" and account["status"] == "Active":
            if repository.active_admin_count(exclude_account_id=account_id) == 0:
                raise ValueError("This account cannot be moved to a non admin profile because it is the last active User Admin account.")
        return repository.update(
            account_id,
            display_name.strip(),
            email.strip(),
            profile_id,
        )

    @classmethod
    def suspend_account(cls, account_id):
        from .repositories import AccountRepository
        repository = AccountRepository()
        account = repository.get(account_id)
        if not account:
            raise ValueError("Account not found.")
        if account["role"] == "User Admin" and account["status"] == "Active":
            if repository.active_admin_count(exclude_account_id=account_id) == 0:
                raise ValueError("This account cannot be suspended because it is the last active User Admin account.")
        return repository.suspend(account_id)

    @classmethod
    def reactivate_account(cls, account_id):
        from .repositories import AccountRepository
        repository = AccountRepository()
        account = repository.get(account_id)
        if not account:
            raise ValueError("Account not found.")
        return repository.reactivate(account_id)

    @classmethod
    def find_by_username(cls, username):
        from .repositories import AccountRepository
        return AccountRepository().by_username(username)

    @classmethod
    def access_state(cls, account_id):
        from .repositories import AccountRepository
        return AccountRepository().access_state(account_id)

    @classmethod
    def verify_password(cls, account, password):
        if not account:
            return False
        return check_password_hash(account["password_hash"], password)


@dataclass
class Session:
    session_id: Optional[int]
    account_id: int
    role: str
    created_at: str
    active: bool = True

    @classmethod
    def create_session(cls, account_id, role):
        from .repositories import SessionRepository
        return SessionRepository().create(account_id, role)

    @classmethod
    def invalidate_session(cls, session_id):
        from .repositories import SessionRepository
        return SessionRepository().invalidate(session_id)

    @classmethod
    def is_active(cls, session_id):
        from .repositories import SessionRepository
        return SessionRepository().active(session_id) is not None


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

    @classmethod
    def create_company(cls, designer_id, data):
        from .repositories import CompanyRepository
        return CompanyRepository().create(
            designer_id,
            data.get("name", "").strip(),
            data.get("description", "").strip(),
            data.get("phone", "").strip(),
            data.get("email", "").strip(),
            data.get("website", "").strip(),
            data.get("address", "").strip(),
        )

    @classmethod
    def get_company(cls, designer_id):
        from .repositories import CompanyRepository
        return CompanyRepository().get_for_designer(designer_id)

    @classmethod
    def update_company(cls, designer_id, data):
        from .repositories import CompanyRepository
        return CompanyRepository().update(
            designer_id,
            data.get("name", "").strip(),
            data.get("description", "").strip(),
            data.get("phone", "").strip(),
            data.get("email", "").strip(),
            data.get("website", "").strip(),
            data.get("address", "").strip(),
        )

    @classmethod
    def delete_company(cls, designer_id):
        from .repositories import CompanyRepository
        return CompanyRepository().delete(designer_id)

    @classmethod
    def search_company(cls, designer_id, keyword=""):
        from .repositories import CompanyRepository
        return CompanyRepository().search(designer_id, keyword)


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

    @classmethod
    def create_project(cls, designer_id, data, project_status):
        from .repositories import ProjectRepository, ActivityRepository
        project_id = ProjectRepository().create(
            designer_id,
            int(data["category_id"]),
            data["title"].strip(),
            data["description"].strip(),
            project_status,
            int(data.get("progress", 0)),
            data.get("image_url", "").strip(),
        )
        ActivityRepository().log("project_created", designer_id, project_id)
        return project_id

    @classmethod
    def get_owned_projects(cls, designer_id, project_status):
        from .repositories import ProjectRepository
        return ProjectRepository().search_owned(designer_id, project_status, "")

    @classmethod
    def search_owned_projects(cls, designer_id, project_status, keyword=""):
        from .repositories import ProjectRepository
        return ProjectRepository().search_owned(designer_id, project_status, keyword)

    @classmethod
    def update_owned_project(cls, project_id, designer_id, data, project_status):
        from .repositories import ProjectRepository
        return ProjectRepository().update_owned(
            project_id,
            designer_id,
            int(data["category_id"]),
            data["title"].strip(),
            data["description"].strip(),
            project_status,
            int(data.get("progress", 0)),
            data.get("image_url", "").strip(),
        )

    @classmethod
    def delete_owned_project(cls, project_id, designer_id, project_status):
        from .repositories import ProjectRepository
        return ProjectRepository().delete_owned(project_id, designer_id, project_status)

    @classmethod
    def search_available_projects(cls, keyword=""):
        from .repositories import ProjectRepository
        return ProjectRepository().search_available(keyword)

    @classmethod
    def get_available_project(cls, project_id):
        from .repositories import ProjectRepository
        project = ProjectRepository().get(project_id)
        if not project or not project["visible"] or project["category_status"] != "Active":
            return None
        return project

    @classmethod
    def record_view(cls, project_id, customer_id):
        from .repositories import ProjectRepository, ActivityRepository
        ProjectRepository().add_view(project_id, customer_id)
        ActivityRepository().log("project_viewed", customer_id, project_id)

    @classmethod
    def get_designer_projects_with_metrics(cls, designer_id):
        from .repositories import ProjectRepository
        return ProjectRepository().all_owned(designer_id)


@dataclass
class Favourite:
    favourite_id: Optional[int]
    customer_id: int
    project_id: int
    saved_at: str

    @classmethod
    def save_project(cls, customer_id, project_id):
        from .repositories import FavouriteRepository, ActivityRepository
        project = IDP.get_available_project(project_id)
        if not project:
            return False
        added = FavouriteRepository().add_available(customer_id, project_id)
        if added:
            ActivityRepository().log("project_shortlisted", customer_id, project_id)
        return bool(added)

    @classmethod
    def search_saved_projects(cls, customer_id, keyword=""):
        from .repositories import FavouriteRepository
        return FavouriteRepository().search(customer_id, keyword)

    @classmethod
    def view_saved_projects(cls, customer_id):
        from .repositories import FavouriteRepository
        return FavouriteRepository().search(customer_id, "")

    @classmethod
    def remove_project(cls, customer_id, project_id):
        from .repositories import FavouriteRepository, ActivityRepository
        removed = FavouriteRepository().remove(customer_id, project_id)
        if removed:
            ActivityRepository().log("project_unshortlisted", customer_id, project_id)
        return bool(removed)

    @classmethod
    def is_saved(cls, customer_id, project_id):
        from .repositories import FavouriteRepository
        return FavouriteRepository().exists(customer_id, project_id)


@dataclass
class IDPCategory:
    category_id: Optional[int]
    name: str
    description: str
    status: str = "Active"

    @classmethod
    def create_category(cls, name, description=""):
        from .repositories import CategoryRepository
        repository = CategoryRepository()
        name = " ".join(name.split())
        if repository.find_by_name(name):
            raise ValueError("A category with this name already exists.")
        return repository.create(name, description.strip())

    @classmethod
    def get_category(cls, category_id):
        from .repositories import CategoryRepository
        return CategoryRepository().get(category_id)

    @classmethod
    def get_categories(cls, active_only=False):
        from .repositories import CategoryRepository
        return CategoryRepository().search("", active_only)

    @classmethod
    def update_category(cls, category_id, name, description=""):
        from .repositories import CategoryRepository
        return CategoryRepository().update(category_id, name.strip(), description.strip())

    @classmethod
    def suspend_category(cls, category_id):
        from .repositories import CategoryRepository
        return CategoryRepository().suspend(category_id)

    @classmethod
    def reactivate_category(cls, category_id):
        from .repositories import CategoryRepository
        return CategoryRepository().reactivate(category_id)

    @classmethod
    def delete_category(cls, category_id):
        from .repositories import CategoryRepository
        repository = CategoryRepository()
        category = repository.get(category_id)
        if not category:
            raise ValueError("Category not found.")
        if repository.project_count(category_id) > 0:
            raise ValueError("This category is used by one or more projects. Suspend it instead of deleting it.")
        return repository.delete(category_id)

    @classmethod
    def search_categories(cls, keyword=""):
        from .repositories import CategoryRepository
        return CategoryRepository().search(keyword)


@dataclass
class ActivityEvent:
    event_id: Optional[int]
    event_type: str
    account_id: Optional[int]
    project_id: Optional[int]
    created_at: str

    @classmethod
    def report_between(cls, start, end):
        from .repositories import ActivityRepository
        return ActivityRepository().report(start.isoformat(), end.isoformat())


@dataclass
class ViewMetric:
    project_id: int
    views: int

    @classmethod
    def for_designer(cls, designer_id):
        return IDP.get_designer_projects_with_metrics(designer_id)


@dataclass
class ShortlistMetric:
    project_id: int
    shortlists: int

    @classmethod
    def for_designer(cls, designer_id):
        return IDP.get_designer_projects_with_metrics(designer_id)


@dataclass
class ReportSummary:
    period_label: str
    users: int
    projects: int
    views: int
    shortlists: int

    @classmethod
    def _selected_date(cls, date_value):
        now = datetime.utcnow()
        if not date_value:
            return now
        try:
            return datetime.fromisoformat(date_value)
        except ValueError:
            return now

    @classmethod
    def _build(cls, period, start, end, selected):
        now = datetime.utcnow()
        if end > now:
            end = now
        row = ActivityEvent.report_between(start, end)
        return {
            "period": period,
            "from": start.date().isoformat(),
            "to": end.date().isoformat(),
            "selected": selected.date().isoformat(),
            **dict(row),
        }


@dataclass
class DailyReport(ReportSummary):
    @classmethod
    def generate(cls, date_value=None):
        selected = cls._selected_date(date_value)
        start = selected.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1) - timedelta(microseconds=1)
        return cls._build("Daily", start, end, selected)


@dataclass
class WeeklyReport(ReportSummary):
    @classmethod
    def generate(cls, date_value=None):
        selected = cls._selected_date(date_value)
        start = (selected - timedelta(days=selected.weekday())).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end = start + timedelta(days=7) - timedelta(microseconds=1)
        return cls._build("Weekly", start, end, selected)


@dataclass
class MonthlyReport(ReportSummary):
    @classmethod
    def generate(cls, date_value=None):
        selected = cls._selected_date(date_value)
        start = selected.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(microseconds=1)
        return cls._build("Monthly", start, end, selected)
