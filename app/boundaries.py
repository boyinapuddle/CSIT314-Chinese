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
    DeleteUserProfileController,
    GenerateDailyReportController,
    GenerateMonthlyReportController,
    GenerateWeeklyReportController,
    InteriorDesignerLogoutController,
    PlatformManagerLogoutController,
    BrowseIDPController,
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


# User Story 11 (User Admin Login)
# User Story 18 (Interior Designer Login)
# User Story 35 (Customer Login)
# User Story 47 (Platform Manager Login)
class LoginBoundary:
    def submit(self, form):
        return AuthenticationController().login(form["username"], form["password"])


# User Story 1 (Create User Profile)
class CreateUserProfileBoundary:
    def submit(self, form):
        return CreateUserProfileController().create(
            form["name"],
            form.get("description", ""),
            form["role"],
        )


# User Story 2 (View User Profile)
class ViewUserProfileBoundary:
    def request(self, profile_id):
        return ViewUserProfileController().view(profile_id)


# User Story 3 (Update User Profile)
class UpdateUserProfileBoundary:
    def submit(self, profile_id, form):
        return UpdateUserProfileController().update(
            profile_id,
            form["name"],
            form.get("description", ""),
            form["role"],
        )


# User Story 4 (Suspend and Reactivate User Profile)
class SuspendUserProfileBoundary:
    def submit(self, profile_id):
        return SuspendUserProfileController().suspend(profile_id)

    def reactivate(self, profile_id):
        return SuspendUserProfileController().reactivate(profile_id)


# User Story 49 (Delete User Profile)
class DeleteUserProfileBoundary:
    def submit(self, profile_id):
        return DeleteUserProfileController().delete(profile_id)


# User Story 5 (Search User Profile)
class SearchUserProfileBoundary:
    def submit(self, keyword=""):
        return SearchUserProfileController().search(keyword)


# User Story 6 (Create User Account)
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


# User Story 7 (View User Account)
class ViewUserAccountBoundary:
    def request(self, account_id):
        return ViewUserAccountController().view(account_id)


# User Story 8 (Update User Account)
class UpdateUserAccountBoundary:
    def submit(self, account_id, form):
        return UpdateUserAccountController().update(
            account_id,
            form["display_name"],
            form["email"],
            int(form["profile_id"]),
        )


# User Story 9 (Suspend and Reactivate User Account)
class SuspendUserAccountBoundary:
    def submit(self, account_id):
        return SuspendUserAccountController().suspend(account_id)

    def reactivate(self, account_id):
        return SuspendUserAccountController().reactivate(account_id)


# User Story 10 (Search User Account)
class SearchUserAccountBoundary:
    def submit(self, keyword=""):
        return SearchUserAccountController().search(keyword)


# User Story 12 (User Admin Logout)
class UserAdminLogoutBoundary:
    def submit(self, session_context):
        return UserAdminLogoutController().logout(_context(session_context))


# User Story 13 (Create Company Information)
class CreateCompanyInformationBoundary:
    def submit(self, session_context, form):
        return CreateCompanyInformationController().create(_context(session_context), form)


# User Story 14 (View Company Information)
class ViewCompanyInformationBoundary:
    def request(self, session_context):
        return ViewCompanyInformationController().view(_context(session_context))


# User Story 15 (Update Company Information)
class UpdateCompanyInformationBoundary:
    def submit(self, session_context, form):
        return UpdateCompanyInformationController().update(_context(session_context), form)


# User Story 16 (Delete Company Information)
class DeleteCompanyInformationBoundary:
    def submit(self, session_context):
        return DeleteCompanyInformationController().delete(_context(session_context))


# User Story 17 (Search Company Information)
class SearchCompanyInformationBoundary:
    def submit(self, session_context, keyword=""):
        return SearchCompanyInformationController().search(_context(session_context), keyword)


# User Story 19 (Interior Designer Logout)
class InteriorDesignerLogoutBoundary:
    def submit(self, session_context):
        return InteriorDesignerLogoutController().logout(_context(session_context))


# User Story 20 (Create Current IDP)
class CreateCurrentIDPBoundary:
    def submit(self, session_context, form):
        return CreateCurrentIDPController().create(_context(session_context), form)

    def categories(self):
        return CreateCurrentIDPController().categories()


# User Story 21 (View Current IDP)
class ViewCurrentIDPBoundary:
    def request(self, session_context):
        return ViewCurrentIDPController().view(_context(session_context))


# User Story 22 (Update Current IDP)
class UpdateCurrentIDPBoundary:
    def submit(self, session_context, project_id, form):
        return UpdateCurrentIDPController().update(_context(session_context), project_id, form)


# User Story 23 (Delete Current IDP)
class DeleteCurrentIDPBoundary:
    def submit(self, session_context, project_id):
        return DeleteCurrentIDPController().delete(_context(session_context), project_id)


# User Story 24 (Search Current IDP)
class SearchCurrentIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchCurrentIDPController().search(_context(session_context), keyword)


# User Story 25 (Create Past IDP)
class CreatePastIDPBoundary:
    def submit(self, session_context, form):
        return CreatePastIDPController().create(_context(session_context), form)

    def categories(self):
        return CreatePastIDPController().categories()


# User Story 26 (View Past IDP)
class ViewPastIDPBoundary:
    def request(self, session_context):
        return ViewPastIDPController().view(_context(session_context))


# User Story 27 (Update Past IDP)
class UpdatePastIDPBoundary:
    def submit(self, session_context, project_id, form):
        return UpdatePastIDPController().update(_context(session_context), project_id, form)


# User Story 28 (Delete Past IDP)
class DeletePastIDPBoundary:
    def submit(self, session_context, project_id):
        return DeletePastIDPController().delete(_context(session_context), project_id)


# User Story 29 (Search Past IDP)
class SearchPastIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchPastIDPController().search(_context(session_context), keyword)


# User Story 30 (Search Available IDP)
class SearchAvailableIDPBoundary:
    def submit(self, keyword=""):
        return SearchAvailableIDPController().search(keyword)


# User Story 31 (View Available IDP)
class ViewAvailableIDPBoundary:
    def request(self, session_context, project_id):
        return ViewAvailableIDPController().view(_context(session_context), project_id)


# User Story 50 (Browse IDPs as Authenticated Non Customer)
class BrowseIDPBoundary:
    def submit(self, session_context, keyword=""):
        return BrowseIDPController().search(_context(session_context), keyword)

    def request(self, session_context, project_id):
        return BrowseIDPController().view(_context(session_context), project_id)


# User Story 32 (Save and Unsave IDP)
class SaveIDPBoundary:
    def submit(self, session_context, project_id):
        return SaveIDPController().save(_context(session_context), project_id)

    def unsave(self, session_context, project_id):
        return SaveIDPController().unsave(_context(session_context), project_id)

    def check_saved(self, session_context, project_id):
        return SaveIDPController().check_saved(_context(session_context), project_id)


# User Story 33 (Search Saved IDP)
class SearchSavedIDPBoundary:
    def submit(self, session_context, keyword=""):
        return SearchSavedIDPController().search(_context(session_context), keyword)


# User Story 34 (View Saved IDP)
class ViewSavedIDPBoundary:
    def request(self, session_context):
        return ViewSavedIDPController().view(_context(session_context))


# User Story 36 (Customer Logout)
class CustomerLogoutBoundary:
    def submit(self, session_context):
        return CustomerLogoutController().logout(_context(session_context))


# User Story 37 (View IDP View Count)
class ViewIDPViewsBoundary:
    def request(self, session_context):
        return ViewIDPViewsController().view(_context(session_context))


# User Story 38 (View IDP Shortlist Count)
class ViewIDPShortlistsBoundary:
    def request(self, session_context):
        return ViewIDPShortlistsController().view(_context(session_context))


# User Story 39 (Create IDP Category)
class CreateIDPCategoryBoundary:
    def submit(self, form):
        return CreateIDPCategoryController().create(form["name"], form.get("description", ""))


# User Story 40 (View IDP Category)
class ViewIDPCategoryBoundary:
    def request(self, category_id):
        return ViewIDPCategoryController().view(category_id)

    def request_all(self):
        return ViewIDPCategoryController().view_all()


# User Story 41 (Update IDP Category)
class UpdateIDPCategoryBoundary:
    def submit(self, category_id, form):
        return UpdateIDPCategoryController().update(category_id, form["name"], form.get("description", ""))


# User Story 42 (Suspend Reactivate and Delete IDP Category)
class SuspendIDPCategoryBoundary:
    def submit(self, category_id):
        return SuspendIDPCategoryController().suspend(category_id)

    def reactivate(self, category_id):
        return SuspendIDPCategoryController().reactivate(category_id)

    def delete(self, category_id):
        return SuspendIDPCategoryController().delete(category_id)


# User Story 43 (Search IDP Category)
class SearchIDPCategoryBoundary:
    def submit(self, keyword=""):
        return SearchIDPCategoryController().search(keyword)


# User Story 44 (Generate Daily Report)
class GenerateDailyReportBoundary:
    def submit(self, date_value=None):
        return GenerateDailyReportController().generate(date_value)


# User Story 45 (Generate Weekly Report)
class GenerateWeeklyReportBoundary:
    def submit(self, date_value=None):
        return GenerateWeeklyReportController().generate(date_value)


# User Story 46 (Generate Monthly Report)
class GenerateMonthlyReportBoundary:
    def submit(self, date_value=None):
        return GenerateMonthlyReportController().generate(date_value)


# User Story 48 (Platform Manager Logout)
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
    49: DeleteUserProfileBoundary,
    50: BrowseIDPBoundary,
}
