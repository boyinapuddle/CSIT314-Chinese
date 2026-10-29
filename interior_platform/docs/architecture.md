# Architecture and class inventory

The implementation follows the Boundary-Control-Entity (BCE) direction used in the supplied user stories and diagrams. **Every user story now has its own unique Control/Controller class.** Shared services and repositories remain underneath those controls so business rules and SQLite access are not duplicated.

## Class count

- Story-specific Controllers: **48 classes (one per user story)**
- Entities: 14 classes
- Repositories: 9 classes
- Services: 12 classes
- Boundaries: 8 classes
- Total: **91 classes**

The 48 controllers are intentionally use-case specific; the remaining classes provide reusable domain, persistence, service, and UI-boundary responsibilities.

## BCE direction

Typical request flow:

`HTML/Jinja Boundary -> Story-specific Controller -> Service -> Repository -> Entity/SQLite`

Examples:

- `AdminBoundary -> CreateUserProfileController -> ProfileService -> ProfileRepository -> UserProfile`
- `DesignerPortfolioBoundary -> SearchPastIDPController -> ProjectService -> ProjectRepository -> IDP`
- `CustomerExploreBoundary -> ViewAvailableIDPController -> ProjectService -> ProjectRepository -> IDP`
- `FavouriteBoundary -> SaveIDPController -> FavouriteService -> FavouriteRepository -> Favourite`
- `PlatformBoundary -> GenerateWeeklyReportController -> ReportService -> ActivityRepository`

## 1:1 user story to Control class mapping

| User story | Dedicated controller |
|---:|---|
| 1 | `CreateUserProfileController` |
| 2 | `ViewUserProfileController` |
| 3 | `UpdateUserProfileController` |
| 4 | `SuspendUserProfileController` |
| 5 | `SearchUserProfileController` |
| 6 | `CreateUserAccountController` |
| 7 | `ViewUserAccountController` |
| 8 | `UpdateUserAccountController` |
| 9 | `SuspendUserAccountController` |
| 10 | `SearchUserAccountController` |
| 11 | `UserAdminLoginController` |
| 12 | `UserAdminLogoutController` |
| 13 | `CreateCompanyInformationController` |
| 14 | `ViewCompanyInformationController` |
| 15 | `UpdateCompanyInformationController` |
| 16 | `DeleteCompanyInformationController` |
| 17 | `SearchCompanyInformationController` |
| 18 | `InteriorDesignerLoginController` |
| 19 | `InteriorDesignerLogoutController` |
| 20 | `CreateCurrentIDPController` |
| 21 | `ViewCurrentIDPController` |
| 22 | `UpdateCurrentIDPController` |
| 23 | `DeleteCurrentIDPController` |
| 24 | `SearchCurrentIDPController` |
| 25 | `CreatePastIDPController` |
| 26 | `ViewPastIDPController` |
| 27 | `UpdatePastIDPController` |
| 28 | `DeletePastIDPController` |
| 29 | `SearchPastIDPController` |
| 30 | `SearchAvailableIDPController` |
| 31 | `ViewAvailableIDPController` |
| 32 | `SaveIDPController` |
| 33 | `SearchSavedIDPController` |
| 34 | `ViewSavedIDPController` |
| 35 | `CustomerLoginController` |
| 36 | `CustomerLogoutController` |
| 37 | `ViewIDPViewsController` |
| 38 | `ViewIDPShortlistsController` |
| 39 | `CreateIDPCategoryController` |
| 40 | `ViewIDPCategoryController` |
| 41 | `UpdateIDPCategoryController` |
| 42 | `SuspendIDPCategoryController` |
| 43 | `SearchIDPCategoryController` |
| 44 | `GenerateDailyReportController` |
| 45 | `GenerateWeeklyReportController` |
| 46 | `GenerateMonthlyReportController` |
| 47 | `PlatformManagerLoginController` |
| 48 | `PlatformManagerLogoutController` |

## Shared-layer rationale

A unique controller does **not** mean copying SQL or validation 48 times. The controller represents the BCE **Control** for one user story, while services/repositories are shared where the underlying domain rule is the same. This keeps direct traceability to the sequence/BCE diagrams while preserving maintainable code.

## Security/business rules reflected from stories

- Role is resolved from the account's linked profile, never trusted from editable form input.
- Each role's login/logout story has its own controller.
- Designer/customer identifiers are read from the authenticated Flask session.
- Suspended accounts or profiles cannot authenticate.
- A favourite uses a unique `(customer_id, project_id)` constraint to prevent duplicates.
- Owned project update/delete SQL includes `designer_id`.
- Past/current deletion also includes project status in the predicate.
- Customer project view only shows visible projects and captures a view on successful detail access.
- Category suspension removes the category from active category choices while preserving historical links.
- Reports are read-only aggregations and daily/weekly/monthly generation have separate controllers.

## Traceability test

`tests/test_story_controllers.py` automatically checks that stories 1-48 are all present, mapped to 48 distinct controller classes, and follow the controller naming convention. This is suitable as a CI regression check if later refactoring accidentally removes or reuses a story controller.
