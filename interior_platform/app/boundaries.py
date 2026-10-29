from .controllers import (
    AuthenticationController,
    CreateCompanyInformationController,
    CreateCurrentIDPController,
    CreateIDPCategoryController,
    CreatePastIDPController,
    CreateUserAccountController,
    CreateUserProfileController,
    CustomerLogoutController,
    DeleteCompanyInformationController,
    DeleteCurrentIDPController,
    DeletePastIDPController,
    GenerateDailyReportController,
    GenerateMonthlyReportController,
    GenerateWeeklyReportController,
    InteriorDesignerLogoutController,
    PlatformManagerLogoutController,
    SaveIDPController,
    SearchAvailableIDPController,
    SearchCompanyInformationController,
    SearchCurrentIDPController,
    SearchIDPCategoryController,
    SearchPastIDPController,
    SearchSavedIDPController,
    SearchUserAccountController,
    SearchUserProfileController,
    SuspendIDPCategoryController,
    SuspendUserAccountController,
    SuspendUserProfileController,
    UpdateCompanyInformationController,
    UpdateCurrentIDPController,
    UpdateIDPCategoryController,
    UpdatePastIDPController,
    UpdateUserAccountController,
    UpdateUserProfileController,
    UserAdminLogoutController,
    ViewAvailableIDPController,
    ViewCompanyInformationController,
    ViewCurrentIDPController,
    ViewIDPCategoryController,
    ViewIDPShortlistsController,
    ViewIDPViewsController,
    ViewPastIDPController,
    ViewSavedIDPController,
    ViewUserAccountController,
    ViewUserProfileController,
)


def _context(session_context):
    return dict(session_context)


class LoginBoundary:
    def submit(self, form):
        return AuthenticationController().login(form["username"], form["password"])


class CreateUserProfileBoundary:
    def submit(self, form):
        return CreateUserProfileController().create(form["name"], form.get("description", ""))


class ViewUserProfileBoundary:
    def request(self, profile_id):
        return ViewUserProfileController().view(profile_id)


class UpdateUserProfileBoundary:
    def submit(self, profile_id, form):
        return UpdateUserProfileController().update(profile_id, form["name"], form.get("description", ""))


class SuspendUserProfileBoundary:
    def submit(self, profile_id):
        return SuspendUserProfileController().suspend(profile_id)


class SearchUserProfileBoundary:
    def submit(self, keyword=""):
        return SearchUserProfileController().search(keyword)


class CreateUserAccountBoundary:
    def submit(self, form):
        return CreateUserAccountController().create(
            form["username"],
            form["password"],
            int(form["profile_id"]),
            form["display_name"],
            form["email"],
        )

    def profiles(self):
        return CreateUserAccountController().profiles()


class ViewUserAccountBoundary:
    def request(self, account_id):
        return ViewUserAccountController().view(account_id)


class UpdateUserAccountBoundary:
    def submit(self, account_id, form):
        return UpdateUserAccountController().update(
            account_id,
            form["display_name"],
            form["email"],
            int(form["profile_id"]),
        )


class SuspendUserAccountBoundary:
    def submit(self, account_id):
        return SuspendUserAccountController().suspend(account_id)


class SearchUserAccountBoundary:
    def submit(self, keyword=""):
        return SearchUserAccountController().search(keyword)


class UserAdminLogoutBoundary:
    def submit(self, session_context):
        return UserAdminLogoutController().logout(_context(session_context))


class CreateCompanyInformationBoundary:
    def submit(self, session_context, form):
        return CreateCompanyInformationController().create(_context(session_context), form)


class ViewCompanyInformationBoundary:
    def request(self, session_context):
        return ViewCompanyInformationController().view(_context(session_context))


class UpdateCompanyInformationBoundary:
    def submit(self, session_context, form):
        return UpdateCompanyInformationController().update(_context(session_context), form)


class DeleteCompanyInformationBoundary:
    def submit(self, session_context):
        return DeleteCompanyInformationController().delete(_context(session_context))


class SearchCompanyInformationBoundary:
    def submit(self, session_context, keyword=""):
        return SearchCompanyInformationController().search(_context(session_context), keyword)


class InteriorDesignerLogoutBoundary:
    def submit(self, session_context):
        return InteriorDesignerLogoutController().logout(_context(session_context))


class CreateCurrentIDPBoundary:
    def submit(self, session_context, form):
        return CreateCurrentIDPController().create(_context(session_context), form)

    def categories(self):
        return CreateCurrentIDPController().categories()


class ViewCurrentIDPBoundary:
    def request(self, session_context):
        return ViewCurrentIDPController().view(_context(session_context))


class UpdateCurrentIDPBoundary:
    def submit(self, session_context, project_id, form):
        return UpdateCurrentIDPController().update(_context(session_context), project_id, form)


class DeleteCurrentIDPBoundary:
    def submit(self, session_context, project_id):
        return DeleteCurrentIDPController().delete(_context(session_context), project_id)


class SearchCurrentIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchCurrentIDPController().search(_context(session_context), keyword)


class CreatePastIDPBoundary:
    def submit(self, session_context, form):
        return CreatePastIDPController().create(_context(session_context), form)

    def categories(self):
        return CreatePastIDPController().categories()


class ViewPastIDPBoundary:
    def request(self, session_context):
        return ViewPastIDPController().view(_context(session_context))


class UpdatePastIDPBoundary:
    def submit(self, session_context, project_id, form):
        return UpdatePastIDPController().update(_context(session_context), project_id, form)


class DeletePastIDPBoundary:
    def submit(self, session_context, project_id):
        return DeletePastIDPController().delete(_context(session_context), project_id)


class SearchPastIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchPastIDPController().search(_context(session_context), keyword)


class SearchAvailableIDPBoundary:
    def submit(self, keyword=""):
        return SearchAvailableIDPController().search(keyword)


class ViewAvailableIDPBoundary:
    def request(self, session_context, project_id):
        return ViewAvailableIDPController().view(_context(session_context), project_id)


class SaveIDPBoundary:
    def submit(self, session_context, project_id):
        return SaveIDPController().save(_context(session_context), project_id)


class SearchSavedIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchSavedIDPController().search(_context(session_context), keyword)


class ViewSavedIDPBoundary:
    def request(self, session_context):
        return ViewSavedIDPController().view(_context(session_context))


class CustomerLogoutBoundary:
    def submit(self, session_context):
        return CustomerLogoutController().logout(_context(session_context))


class ViewIDPViewsBoundary:
    def request(self, session_context):
        return ViewIDPViewsController().view(_context(session_context))


class ViewIDPShortlistsBoundary:
    def request(self, session_context):
        return ViewIDPShortlistsController().view(_context(session_context))


class CreateIDPCategoryBoundary:
    def submit(self, form):
        return CreateIDPCategoryController().create(form["name"], form.get("description", ""))


class ViewIDPCategoryBoundary:
    def request(self, category_id):
        return ViewIDPCategoryController().view(category_id)

    def request_all(self):
        return ViewIDPCategoryController().view_all()


class UpdateIDPCategoryBoundary:
    def submit(self, category_id, form):
        return UpdateIDPCategoryController().update(category_id, form["name"], form.get("description", ""))


class SuspendIDPCategoryBoundary:
    def submit(self, category_id):
        return SuspendIDPCategoryController().suspend(category_id)


class SearchIDPCategoryBoundary:
    def submit(self, keyword=""):
        return SearchIDPCategoryController().search(keyword)


class GenerateDailyReportBoundary:
    def submit(self, date_value=None):
        return GenerateDailyReportController().generate(date_value)


class GenerateWeeklyReportBoundary:
    def submit(self, date_value=None):
        return GenerateWeeklyReportController().generate(date_value)


class GenerateMonthlyReportBoundary:
    def submit(self, date_value=None):
        return GenerateMonthlyReportController().generate(date_value)


class PlatformManagerLogoutBoundary:
    def submit(self, session_context):
        return PlatformManagerLogoutController().logout(_context(session_context))


STORY_BOUNDARIES = {
    1: CreateUserProfileBoundary,
    2: ViewUserProfileBoundary,
    3: UpdateUserProfileBoundary,
    4: SuspendUserProfileBoundary,
    5: SearchUserProfileBoundary,
    6: CreateUserAccountBoundary,
    7: ViewUserAccountBoundary,
    8: UpdateUserAccountBoundary,
    9: SuspendUserAccountBoundary,
    10: SearchUserAccountBoundary,
    11: LoginBoundary,
    12: UserAdminLogoutBoundary,
    13: CreateCompanyInformationBoundary,
    14: ViewCompanyInformationBoundary,
    15: UpdateCompanyInformationBoundary,
    16: DeleteCompanyInformationBoundary,
    17: SearchCompanyInformationBoundary,
    18: LoginBoundary,
    19: InteriorDesignerLogoutBoundary,
    20: CreateCurrentIDPBoundary,
    21: ViewCurrentIDPBoundary,
    22: UpdateCurrentIDPBoundary,
    23: DeleteCurrentIDPBoundary,
    24: SearchCurrentIDPBoundary,
    25: CreatePastIDPBoundary,
    26: ViewPastIDPBoundary,
    27: UpdatePastIDPBoundary,
    28: DeletePastIDPBoundary,
    29: SearchPastIDPBoundary,
    30: SearchAvailableIDPBoundary,
    31: ViewAvailableIDPBoundary,
    32: SaveIDPBoundary,
    33: SearchSavedIDPBoundary,
    34: ViewSavedIDPBoundary,
    35: LoginBoundary,
    36: CustomerLogoutBoundary,
    37: ViewIDPViewsBoundary,
    38: ViewIDPShortlistsBoundary,
    39: CreateIDPCategoryBoundary,
    40: ViewIDPCategoryBoundary,
    41: UpdateIDPCategoryBoundary,
    42: SuspendIDPCategoryBoundary,
    43: SearchIDPCategoryBoundary,
    44: GenerateDailyReportBoundary,
    45: GenerateWeeklyReportBoundary,
    46: GenerateMonthlyReportBoundary,
    47: LoginBoundary,
    48: PlatformManagerLogoutBoundary,
}
