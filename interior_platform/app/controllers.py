from .services import (
    AuthenticationService, SessionService, ProfileService, AccountService,
    CompanyService, ProjectService, FavouriteService, AnalyticsService,
    CategoryService, ReportService,
)


# Part 1 - User Admin: profiles/accounts/login/logout (US01-US12)
class CreateUserProfileController:  # US01
    def __init__(self): self.service = ProfileService()
    def create(self, name, description=""): return self.service.create(name, description)


class ViewUserProfileController:  # US02
    def __init__(self): self.service = ProfileService()
    def view(self, profile_id): return self.service.get(profile_id)


class UpdateUserProfileController:  # US03
    def __init__(self): self.service = ProfileService()
    def update(self, profile_id, name, description=""): return self.service.update(profile_id, name, description)


class SuspendUserProfileController:  # US04
    def __init__(self): self.service = ProfileService()
    def suspend(self, profile_id): return self.service.suspend(profile_id)


class SearchUserProfileController:  # US05
    def __init__(self): self.service = ProfileService()
    def search(self, keyword=""): return self.service.search(keyword)


class CreateUserAccountController:  # US06
    def __init__(self): self.service = AccountService()
    def create(self, username, password, profile_id, display_name, email):
        return self.service.create(username, password, profile_id, display_name, email)


class ViewUserAccountController:  # US07
    def __init__(self): self.service = AccountService()
    def view(self, account_id): return self.service.get(account_id)


class UpdateUserAccountController:  # US08
    def __init__(self): self.service = AccountService()
    def update(self, account_id, display_name, email, profile_id):
        return self.service.update(account_id, display_name, email, profile_id)


class SuspendUserAccountController:  # US09
    def __init__(self): self.service = AccountService()
    def suspend(self, account_id): return self.service.suspend(account_id)


class SearchUserAccountController:  # US10
    def __init__(self): self.service = AccountService()
    def search(self, keyword=""): return self.service.search(keyword)


class UserAdminLoginController:  # US11
    ROLE = "User Admin"
    def __init__(self): self.service = AuthenticationService()
    def login(self, username, password): return self.service.login(username, password, self.ROLE)


class UserAdminLogoutController:  # US12
    def __init__(self): self.service = SessionService()
    def logout(self, session_id): return self.service.stop(session_id)


# Part 2 - Interior Designer company information/login/logout (US13-US19)
class CreateCompanyInformationController:  # US13
    def __init__(self): self.service = CompanyService()
    def create(self, designer_id, data): return self.service.save(designer_id, data)


class ViewCompanyInformationController:  # US14
    def __init__(self): self.service = CompanyService()
    def view(self, designer_id): return self.service.get(designer_id)


class UpdateCompanyInformationController:  # US15
    def __init__(self): self.service = CompanyService()
    def update(self, designer_id, data): return self.service.save(designer_id, data)


class DeleteCompanyInformationController:  # US16
    def __init__(self): self.service = CompanyService()
    def delete(self, designer_id): return self.service.delete(designer_id)


class SearchCompanyInformationController:  # US17
    def __init__(self): self.service = CompanyService()
    def search(self, designer_id, keyword=""): return self.service.search(designer_id, keyword)


class InteriorDesignerLoginController:  # US18
    ROLE = "Interior Designer"
    def __init__(self): self.service = AuthenticationService()
    def login(self, username, password): return self.service.login(username, password, self.ROLE)


class InteriorDesignerLogoutController:  # US19
    def __init__(self): self.service = SessionService()
    def logout(self, session_id): return self.service.stop(session_id)


# Part 3 - Interior Designer current/past IDP portfolio (US20-US29)
class CreateCurrentIDPController:  # US20
    def __init__(self): self.service = ProjectService()
    def create(self, designer_id, data): return self.service.create(designer_id, data, "Current")


class ViewCurrentIDPController:  # US21
    def __init__(self): self.service = ProjectService()
    def view(self, designer_id, keyword=""): return self.service.owned(designer_id, "Current", keyword)


class UpdateCurrentIDPController:  # US22
    def __init__(self): self.service = ProjectService()
    def update(self, project_id, designer_id, data):
        payload = dict(data); payload["project_status"] = "Current"
        return self.service.update(project_id, designer_id, payload)


class DeleteCurrentIDPController:  # US23
    def __init__(self): self.service = ProjectService()
    def delete(self, project_id, designer_id): return self.service.delete(project_id, designer_id, "Current")


class SearchCurrentIDPController:  # US24
    def __init__(self): self.service = ProjectService()
    def search(self, designer_id, keyword=""): return self.service.owned(designer_id, "Current", keyword)


class CreatePastIDPController:  # US25
    def __init__(self): self.service = ProjectService()
    def create(self, designer_id, data): return self.service.create(designer_id, data, "Past")


class ViewPastIDPController:  # US26
    def __init__(self): self.service = ProjectService()
    def view(self, designer_id, keyword=""): return self.service.owned(designer_id, "Past", keyword)


class UpdatePastIDPController:  # US27
    def __init__(self): self.service = ProjectService()
    def update(self, project_id, designer_id, data):
        payload = dict(data); payload["project_status"] = "Past"
        return self.service.update(project_id, designer_id, payload)


class DeletePastIDPController:  # US28
    def __init__(self): self.service = ProjectService()
    def delete(self, project_id, designer_id): return self.service.delete(project_id, designer_id, "Past")


class SearchPastIDPController:  # US29
    def __init__(self): self.service = ProjectService()
    def search(self, designer_id, keyword=""): return self.service.owned(designer_id, "Past", keyword)


# Part 4 - Customer IDP discovery/favourites/login/logout (US30-US36)
class SearchAvailableIDPController:  # US30
    def __init__(self): self.service = ProjectService()
    def search(self, keyword=""): return self.service.available(keyword)


class ViewAvailableIDPController:  # US31
    def __init__(self): self.service = ProjectService()
    def view(self, project_id, customer_id): return self.service.view(project_id, customer_id)


class SaveIDPController:  # US32
    def __init__(self): self.service = FavouriteService()
    def save(self, customer_id, project_id): return self.service.save(customer_id, project_id)


class SearchSavedIDPController:  # US33
    def __init__(self): self.service = FavouriteService()
    def search(self, customer_id, keyword=""): return self.service.search(customer_id, keyword)


class ViewSavedIDPController:  # US34
    def __init__(self): self.service = FavouriteService()
    def view(self, customer_id): return self.service.search(customer_id, "")


class CustomerLoginController:  # US35
    ROLE = "Customer"
    def __init__(self): self.service = AuthenticationService()
    def login(self, username, password): return self.service.login(username, password, self.ROLE)


class CustomerLogoutController:  # US36
    def __init__(self): self.service = SessionService()
    def logout(self, session_id): return self.service.stop(session_id)


# Part 5 - Interior Designer IDP interest metrics (US37-US38)
class ViewIDPViewsController:  # US37
    def __init__(self): self.service = AnalyticsService()
    def view(self, designer_id): return self.service.designer_metric_rows(designer_id, "views")


class ViewIDPShortlistsController:  # US38
    def __init__(self): self.service = AnalyticsService()
    def view(self, designer_id): return self.service.designer_metric_rows(designer_id, "shortlists")


# Part 6 - Platform Manager categories/reports/login/logout (US39-US48)
class CreateIDPCategoryController:  # US39
    def __init__(self): self.service = CategoryService()
    def create(self, name, description=""): return self.service.create(name, description)


class ViewIDPCategoryController:  # US40
    def __init__(self): self.service = CategoryService()
    def view(self, category_id): return self.service.get(category_id)
    def view_all(self): return self.service.search("")


class UpdateIDPCategoryController:  # US41
    def __init__(self): self.service = CategoryService()
    def update(self, category_id, name, description=""): return self.service.update(category_id, name, description)


class SuspendIDPCategoryController:  # US42
    def __init__(self): self.service = CategoryService()
    def suspend(self, category_id): return self.service.suspend(category_id)


class SearchIDPCategoryController:  # US43
    def __init__(self): self.service = CategoryService()
    def search(self, keyword=""): return self.service.search(keyword)


class GenerateDailyReportController:  # US44
    def __init__(self): self.service = ReportService()
    def generate(self, date_value=None): return self.service.generate("daily", date_value)


class GenerateWeeklyReportController:  # US45
    def __init__(self): self.service = ReportService()
    def generate(self, date_value=None): return self.service.generate("weekly", date_value)


class GenerateMonthlyReportController:  # US46
    def __init__(self): self.service = ReportService()
    def generate(self, date_value=None): return self.service.generate("monthly", date_value)


class PlatformManagerLoginController:  # US47
    ROLE = "Platform Manager"
    def __init__(self): self.service = AuthenticationService()
    def login(self, username, password): return self.service.login(username, password, self.ROLE)


class PlatformManagerLogoutController:  # US48
    def __init__(self): self.service = SessionService()
    def logout(self, session_id): return self.service.stop(session_id)


STORY_CONTROLLERS = {
    1: CreateUserProfileController, 2: ViewUserProfileController,
    3: UpdateUserProfileController, 4: SuspendUserProfileController,
    5: SearchUserProfileController, 6: CreateUserAccountController,
    7: ViewUserAccountController, 8: UpdateUserAccountController,
    9: SuspendUserAccountController, 10: SearchUserAccountController,
    11: UserAdminLoginController, 12: UserAdminLogoutController,
    13: CreateCompanyInformationController, 14: ViewCompanyInformationController,
    15: UpdateCompanyInformationController, 16: DeleteCompanyInformationController,
    17: SearchCompanyInformationController, 18: InteriorDesignerLoginController,
    19: InteriorDesignerLogoutController, 20: CreateCurrentIDPController,
    21: ViewCurrentIDPController, 22: UpdateCurrentIDPController,
    23: DeleteCurrentIDPController, 24: SearchCurrentIDPController,
    25: CreatePastIDPController, 26: ViewPastIDPController,
    27: UpdatePastIDPController, 28: DeletePastIDPController,
    29: SearchPastIDPController, 30: SearchAvailableIDPController,
    31: ViewAvailableIDPController, 32: SaveIDPController,
    33: SearchSavedIDPController, 34: ViewSavedIDPController,
    35: CustomerLoginController, 36: CustomerLogoutController,
    37: ViewIDPViewsController, 38: ViewIDPShortlistsController,
    39: CreateIDPCategoryController, 40: ViewIDPCategoryController,
    41: UpdateIDPCategoryController, 42: SuspendIDPCategoryController,
    43: SearchIDPCategoryController, 44: GenerateDailyReportController,
    45: GenerateWeeklyReportController, 46: GenerateMonthlyReportController,
    47: PlatformManagerLoginController, 48: PlatformManagerLogoutController,
}
