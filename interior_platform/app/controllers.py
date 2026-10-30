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
    UserSession,
    ViewMetric,
    WeeklyReport,
)


def _account_id(session_context):
    return session_context.get("account_id")


def _session_id(session_context):
    return session_context.get("session_id")


ROLE_LOGIN_CONTROLLERS = {}


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
        session_id = UserSession.create_session(account["account_id"], self.role)
        return account, session_id


class CreateUserProfileController:
    def create(self, name, description="", role="Customer"):
        return UserProfile.create_profile(name, description, role)


class ViewUserProfileController:
    def view(self, profile_id):
        return UserProfile.get_profile(profile_id)


class UpdateUserProfileController:
    def update(self, profile_id, name, description="", role="Customer"):
        return UserProfile.update_profile(profile_id, name, description, role)


class SuspendUserProfileController:
    def suspend(self, profile_id):
        return UserProfile.suspend_profile(profile_id)


class ReactivateUserProfileController:
    def reactivate(self, profile_id):
        return UserProfile.reactivate_profile(profile_id)


class DeleteUserProfileController:
    def delete(self, profile_id):
        return UserProfile.delete_profile(profile_id)


class SearchUserProfileController:
    def search(self, keyword=""):
        return UserProfile.search_profiles(keyword)


class CreateUserAccountController:
    def create(self, username, password, profile_id, display_name, email):
        return UserAccount.create_account(username, password, profile_id, display_name, email)

    def profiles(self):
        return UserProfile.search_profiles("")


class ViewUserAccountController:
    def view(self, account_id):
        return UserAccount.get_account(account_id)


class UpdateUserAccountController:
    def update(self, account_id, display_name, email, profile_id):
        return UserAccount.update_account(account_id, display_name, email, profile_id)


class SuspendUserAccountController:
    def suspend(self, account_id):
        return UserAccount.suspend_account(account_id)


class ReactivateUserAccountController:
    def reactivate(self, account_id):
        return UserAccount.reactivate_account(account_id)


class SearchUserAccountController:
    def search(self, keyword=""):
        return UserAccount.search_accounts(keyword)


class UserAdminLoginController(RoleLoginControllerBase):
    role = "User Admin"


class UserAdminLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return UserSession.invalidate_session(session_id)
        return 0


class CreateCompanyInformationController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return Company.create_company(designer_id, data)


class ViewCompanyInformationController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return Company.get_company(designer_id)


class UpdateCompanyInformationController:
    def update(self, session_context, data):
        designer_id = _account_id(session_context)
        return Company.update_company(designer_id, data)


class DeleteCompanyInformationController:
    def delete(self, session_context):
        designer_id = _account_id(session_context)
        return Company.delete_company(designer_id)


class SearchCompanyInformationController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return Company.search_company(designer_id, keyword)


class InteriorDesignerLoginController(RoleLoginControllerBase):
    role = "Interior Designer"


class InteriorDesignerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return UserSession.invalidate_session(session_id)
        return 0


class CreateCurrentIDPController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return IDP.create_project(designer_id, data, "Current")

    def categories(self):
        return IDPCategory.get_categories(True)


class ViewCurrentIDPController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return IDP.get_owned_projects(designer_id, "Current")


class UpdateCurrentIDPController:
    def update(self, session_context, project_id, data):
        designer_id = _account_id(session_context)
        return IDP.update_owned_project(project_id, designer_id, data, "Current")


class DeleteCurrentIDPController:
    def delete(self, session_context, project_id):
        designer_id = _account_id(session_context)
        return IDP.delete_owned_project(project_id, designer_id, "Current")


class SearchCurrentIDPController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return IDP.search_owned_projects(designer_id, "Current", keyword)


class CreatePastIDPController:
    def create(self, session_context, data):
        designer_id = _account_id(session_context)
        return IDP.create_project(designer_id, data, "Past")

    def categories(self):
        return IDPCategory.get_categories(True)


class ViewPastIDPController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return IDP.get_owned_projects(designer_id, "Past")


class UpdatePastIDPController:
    def update(self, session_context, project_id, data):
        designer_id = _account_id(session_context)
        return IDP.update_owned_project(project_id, designer_id, data, "Past")


class DeletePastIDPController:
    def delete(self, session_context, project_id):
        designer_id = _account_id(session_context)
        return IDP.delete_owned_project(project_id, designer_id, "Past")


class SearchPastIDPController:
    def search(self, session_context, keyword=""):
        designer_id = _account_id(session_context)
        return IDP.search_owned_projects(designer_id, "Past", keyword)


class SearchAvailableIDPController:
    def search(self, keyword=""):
        return IDP.search_available_projects(keyword)


class ViewAvailableIDPController:
    def view(self, session_context, project_id):
        account_id = _account_id(session_context)
        role = session_context.get("role")
        project = IDP.get_available_project(project_id)
        if project and role == "Customer":
            IDP.record_view(project_id, account_id)
            project = IDP.get_available_project(project_id)
        return project


class SaveIDPController:
    def save(self, session_context, project_id):
        customer_id = _account_id(session_context)
        return Favourite.save_project(customer_id, project_id)


class UnsaveIDPController:
    def unsave(self, session_context, project_id):
        customer_id = _account_id(session_context)
        return Favourite.remove_project(customer_id, project_id)


class CheckSavedIDPController:
    def check(self, session_context, project_id):
        customer_id = _account_id(session_context)
        return Favourite.is_saved(customer_id, project_id)


class SearchSavedIDPController:
    def search(self, session_context, keyword=""):
        customer_id = _account_id(session_context)
        return Favourite.search_saved_projects(customer_id, keyword)


class ViewSavedIDPController:
    def view(self, session_context):
        customer_id = _account_id(session_context)
        return Favourite.view_saved_projects(customer_id)


class CustomerLoginController(RoleLoginControllerBase):
    role = "Customer"


class CustomerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return UserSession.invalidate_session(session_id)
        return 0


class ViewIDPViewsController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return ViewMetric.for_designer(designer_id)


class ViewIDPShortlistsController:
    def view(self, session_context):
        designer_id = _account_id(session_context)
        return ShortlistMetric.for_designer(designer_id)


class CreateIDPCategoryController:
    def create(self, name, description=""):
        return IDPCategory.create_category(name, description)


class ViewIDPCategoryController:
    def view(self, category_id):
        return IDPCategory.get_category(category_id)

    def view_all(self):
        return IDPCategory.get_categories()


class UpdateIDPCategoryController:
    def update(self, category_id, name, description=""):
        return IDPCategory.update_category(category_id, name, description)


class SuspendIDPCategoryController:
    def suspend(self, category_id):
        return IDPCategory.suspend_category(category_id)


class ReactivateIDPCategoryController:
    def reactivate(self, category_id):
        return IDPCategory.reactivate_category(category_id)


class DeleteIDPCategoryController:
    def delete(self, category_id):
        return IDPCategory.delete_category(category_id)


class SearchIDPCategoryController:
    def search(self, keyword=""):
        return IDPCategory.search_categories(keyword)


class GenerateDailyReportController:
    def generate(self, date_value=None):
        return DailyReport.generate(date_value)


class GenerateWeeklyReportController:
    def generate(self, date_value=None):
        return WeeklyReport.generate(date_value)


class GenerateMonthlyReportController:
    def generate(self, date_value=None):
        return MonthlyReport.generate(date_value)


class PlatformManagerLoginController(RoleLoginControllerBase):
    role = "Platform Manager"


class PlatformManagerLogoutController:
    def logout(self, session_context):
        session_id = _session_id(session_context)
        if session_id:
            return UserSession.invalidate_session(session_id)
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
}
