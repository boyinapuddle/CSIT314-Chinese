from .entities import (
    ActivityEvent,
    Company,
    DailyReport,
    Favourite,
    IDP,
    IDPCategory,
    MonthlyReport,
    ShortlistMetric,
    UserAccount,
    UserProfile,
    Session,
    ViewMetric,
    WeeklyReport,
)


def _account_id(session_context):
    return session_context.get("account_id")


def _session_id(session_context):
    return session_context.get("session_id")


def _require_role(session_context, role):
    if session_context.get("role") != role:
        raise PermissionError(f"{role} access is required.")
    return _account_id(session_context)


def _require_non_customer(session_context):
    if session_context.get("role") == "Customer":
        raise PermissionError("This browse flow is for non customer users only.")


ROLE_LOGIN_CONTROLLERS = {}


# User Story 11 (User Admin Login)
# User Story 18 (Interior Designer Login)
# User Story 35 (Customer Login)
# User Story 47 (Platform Manager Login)
class AuthenticationController:
    def login(self, username, password):
        account = UserAccount.find_by_username(username)
        if not account or account["status"] != "Active":
            return None
        if not UserAccount.verify_password(account, password):
            return None
        profile = UserProfile.get_profile(account["profile_id"])
        if not profile or profile["status"] != "Active":
            return None
        controller_class = ROLE_LOGIN_CONTROLLERS.get(profile["role"])
        if not controller_class:
            return None
        return controller_class().complete_login(account, profile)


class RoleLoginControllerBase:
    role = ""

    def complete_login(self, account, profile):
        if profile["role"] != self.role:
            return None
        session_id = Session.create_session(account["account_id"], self.role)
        return account, session_id


# User Story 1 (Create User Profile)
class CreateUserProfileController:
    def create(self, name, description="", role="Customer"):
        return UserProfile.create_profile(name, description, role)


# User Story 2 (View User Profile)
class ViewUserProfileController:
    def view(self, profile_id):
        return UserProfile.get_profile(profile_id)


# User Story 3 (Update User Profile)
class UpdateUserProfileController:
    def update(self, profile_id, name, description="", role="Customer"):
        return UserProfile.update_profile(profile_id, name, description, role)


# User Story 4 (Suspend and Reactivate User Profile)
class SuspendUserProfileController:
    def suspend(self, profile_id):
        return UserProfile.suspend_profile(profile_id)

    def reactivate(self, profile_id):
        return UserProfile.reactivate_profile(profile_id)


# User Story 49 (Delete User Profile)
class DeleteUserProfileController:
    def delete(self, profile_id):
        return UserProfile.delete_profile(profile_id)


# User Story 5 (Search User Profile)
class SearchUserProfileController:
    def search(self, keyword=""):
        return UserProfile.search_profiles(keyword)


# User Story 6 (Create User Account)
class CreateUserAccountController:
    def create(self, username, password, profile_id, display_name, email):
        return UserAccount.create_account(username, password, profile_id, display_name, email)

    def profiles(self):
        return UserProfile.search_profiles("")


# User Story 7 (View User Account)
class ViewUserAccountController:
    def view(self, account_id):
        return UserAccount.get_account(account_id)


# User Story 8 (Update User Account)
class UpdateUserAccountController:
    def update(self, account_id, display_name, email, profile_id):
        return UserAccount.update_account(account_id, display_name, email, profile_id)


# User Story 9 (Suspend and Reactivate User Account)
class SuspendUserAccountController:
    def suspend(self, account_id):
        return UserAccount.suspend_account(account_id)

    def reactivate(self, account_id):
        return UserAccount.reactivate_account(account_id)


# User Story 10 (Search User Account)
class SearchUserAccountController:
    def search(self, keyword=""):
        return UserAccount.search_accounts(keyword)


# User Story 11 (User Admin Login)
class UserAdminLoginController(RoleLoginControllerBase):
    role = "User Admin"


# User Story 12 (User Admin Logout)
class UserAdminLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return Session.invalidate_session(session_id)
        return 0


# User Story 13 (Create Company Information)
class CreateCompanyInformationController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return Company.create_company(designer_id, data)


# User Story 14 (View Company Information)
class ViewCompanyInformationController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return Company.get_company(designer_id)


# User Story 15 (Update Company Information)
class UpdateCompanyInformationController:
    def update(self, session_context, data):
        designer_id = _account_id(session_context)
        return Company.update_company(designer_id, data)


# User Story 16 (Delete Company Information)
class DeleteCompanyInformationController:
    def delete(self, session_context):
        designer_id = _account_id(session_context)
        return Company.delete_company(designer_id)


# User Story 17 (Search Company Information)
class SearchCompanyInformationController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return Company.search_company(designer_id, keyword)


# User Story 18 (Interior Designer Login)
class InteriorDesignerLoginController(RoleLoginControllerBase):
    role = "Interior Designer"


# User Story 19 (Interior Designer Logout)
class InteriorDesignerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return Session.invalidate_session(session_id)
        return 0


# User Story 20 (Create Current IDP)
class CreateCurrentIDPController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return IDP.create_project(designer_id, data, "Current")

    def categories(self):
        return IDPCategory.get_categories(True)


# User Story 21 (View Current IDP)
class ViewCurrentIDPController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return IDP.get_owned_projects(designer_id, "Current")


# User Story 22 (Update Current IDP)
class UpdateCurrentIDPController:
    def update(self, session_context, project_id, data):
        designer_id = _account_id(session_context)
        return IDP.update_owned_project(project_id, designer_id, data, "Current")


# User Story 23 (Delete Current IDP)
class DeleteCurrentIDPController:
    def delete(self, session_context, project_id):
        designer_id = _account_id(session_context)
        return IDP.delete_owned_project(project_id, designer_id, "Current")


# User Story 24 (Search Current IDP)
class SearchCurrentIDPController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return IDP.search_owned_projects(designer_id, "Current", keyword)


# User Story 25 (Create Past IDP)
class CreatePastIDPController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return IDP.create_project(designer_id, data, "Past")

    def categories(self):
        return IDPCategory.get_categories(True)


# User Story 26 (View Past IDP)
class ViewPastIDPController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return IDP.get_owned_projects(designer_id, "Past")


# User Story 27 (Update Past IDP)
class UpdatePastIDPController:
    def update(self, session_context, project_id, data):
        designer_id = _account_id(session_context)
        return IDP.update_owned_project(project_id, designer_id, data, "Past")


# User Story 28 (Delete Past IDP)
class DeletePastIDPController:
    def delete(self, session_context, project_id):
        designer_id = _account_id(session_context)
        return IDP.delete_owned_project(project_id, designer_id, "Past")


# User Story 29 (Search Past IDP)
class SearchPastIDPController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return IDP.search_owned_projects(designer_id, "Past", keyword)


# User Story 30 (Search Available IDP)
class SearchAvailableIDPController:
    def search(self, keyword=""):
        return IDP.search_available_projects(keyword)


# User Story 31 (View Available IDP)
class ViewAvailableIDPController:
    def view(self, session_context, project_id):
        account_id = _account_id(session_context)
        project = IDP.get_available_project(project_id)
        if project:
            IDP.record_view(project_id, account_id)
            project = IDP.get_available_project(project_id)
        return project


# User Story 50 (Browse IDPs as Authenticated Non Customer)
class BrowseIDPController:
    def search(self, session_context, keyword=""):
        _require_non_customer(session_context)
        return IDP.search_available_projects(keyword)

    def view(self, session_context, project_id):
        _require_non_customer(session_context)
        return IDP.get_available_project(project_id)


# User Story 32 (Save and Unsave IDP)
class SaveIDPController:
    def save(self, session_context, project_id):
        customer_id = _require_role(session_context, "Customer")
        return Favourite.save_project(customer_id, project_id)

    def unsave(self, session_context, project_id):
        customer_id = _require_role(session_context, "Customer")
        return Favourite.remove_project(customer_id, project_id)

    def check_saved(self, session_context, project_id):
        customer_id = _require_role(session_context, "Customer")
        return Favourite.is_saved(customer_id, project_id)


# User Story 33 (Search Saved IDP)
class SearchSavedIDPController:
    def search(self, session_context, keyword=""):
        customer_id = _account_id(session_context)
        return Favourite.search_saved_projects(customer_id, keyword)


# User Story 34 (View Saved IDP)
class ViewSavedIDPController:
    def view(self, session_context):
        customer_id = _account_id(session_context)
        return Favourite.view_saved_projects(customer_id)


# User Story 35 (Customer Login)
class CustomerLoginController(RoleLoginControllerBase):
    role = "Customer"


# User Story 36 (Customer Logout)
class CustomerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return Session.invalidate_session(session_id)
        return 0


# User Story 37 (View IDP View Count)
class ViewIDPViewsController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return ViewMetric.for_designer(designer_id)


# User Story 38 (View IDP Shortlist Count)
class ViewIDPShortlistsController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return ShortlistMetric.for_designer(designer_id)


# User Story 39 (Create IDP Category)
class CreateIDPCategoryController:
    def create(self, name, description=""):
        return IDPCategory.create_category(name, description)


# User Story 40 (View IDP Category)
class ViewIDPCategoryController:
    def view(self, category_id):
        return IDPCategory.get_category(category_id)

    def view_all(self):
        return IDPCategory.get_categories()


# User Story 41 (Update IDP Category)
class UpdateIDPCategoryController:
    def update(self, category_id, name, description=""):
        return IDPCategory.update_category(category_id, name, description)


# User Story 42 (Suspend Reactivate and Delete IDP Category)
class SuspendIDPCategoryController:
    def suspend(self, category_id):
        return IDPCategory.suspend_category(category_id)

    def reactivate(self, category_id):
        return IDPCategory.reactivate_category(category_id)

    def delete(self, category_id):
        return IDPCategory.delete_category(category_id)


# User Story 43 (Search IDP Category)
class SearchIDPCategoryController:
    def search(self, keyword=""):
        return IDPCategory.search_categories(keyword)


# User Story 44 (Generate Daily Report)
class GenerateDailyReportController:
    def generate(self, date_value=None):
        return DailyReport.generate(date_value)


# User Story 45 (Generate Weekly Report)
class GenerateWeeklyReportController:
    def generate(self, date_value=None):
        return WeeklyReport.generate(date_value)


# User Story 46 (Generate Monthly Report)
class GenerateMonthlyReportController:
    def generate(self, date_value=None):
        return MonthlyReport.generate(date_value)


# User Story 47 (Platform Manager Login)
class PlatformManagerLoginController(RoleLoginControllerBase):
    role = "Platform Manager"


# User Story 48 (Platform Manager Logout)
class PlatformManagerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return Session.invalidate_session(session_id)
        return 0


ROLE_LOGIN_CONTROLLERS.update({
    "User Admin": UserAdminLoginController,
    "Interior Designer": InteriorDesignerLoginController,
    "Customer": CustomerLoginController,
    "Platform Manager": PlatformManagerLoginController,
})


STORY_CONTROLLERS = {
    1: CreateUserProfileController,
    2: ViewUserProfileController,
    3: UpdateUserProfileController,
    4: SuspendUserProfileController,
    5: SearchUserProfileController,
    6: CreateUserAccountController,
    7: ViewUserAccountController,
    8: UpdateUserAccountController,
    9: SuspendUserAccountController,
    10: SearchUserAccountController,
    11: UserAdminLoginController,
    12: UserAdminLogoutController,
    13: CreateCompanyInformationController,
    14: ViewCompanyInformationController,
    15: UpdateCompanyInformationController,
    16: DeleteCompanyInformationController,
    17: SearchCompanyInformationController,
    18: InteriorDesignerLoginController,
    19: InteriorDesignerLogoutController,
    20: CreateCurrentIDPController,
    21: ViewCurrentIDPController,
    22: UpdateCurrentIDPController,
    23: DeleteCurrentIDPController,
    24: SearchCurrentIDPController,
    25: CreatePastIDPController,
    26: ViewPastIDPController,
    27: UpdatePastIDPController,
    28: DeletePastIDPController,
    29: SearchPastIDPController,
    30: SearchAvailableIDPController,
    31: ViewAvailableIDPController,
    32: SaveIDPController,
    33: SearchSavedIDPController,
    34: ViewSavedIDPController,
    35: CustomerLoginController,
    36: CustomerLogoutController,
    37: ViewIDPViewsController,
    38: ViewIDPShortlistsController,
    39: CreateIDPCategoryController,
    40: ViewIDPCategoryController,
    41: UpdateIDPCategoryController,
    42: SuspendIDPCategoryController,
    43: SearchIDPCategoryController,
    44: GenerateDailyReportController,
    45: GenerateWeeklyReportController,
    46: GenerateMonthlyReportController,
    47: PlatformManagerLoginController,
    48: PlatformManagerLogoutController,
    49: DeleteUserProfileController,
    50: BrowseIDPController,
}
