# Architecture and class inventory

The application follows a Boundary Control Entity structure for the documented use cases and sequence flows.

## Program flow

The normal use case flow is

`Browser or actor -> Flask route -> Story Boundary -> Story Controller -> Entity -> Repository -> SQLite`

The result returns through the same use case layers

`SQLite -> Repository -> Entity -> Story Controller -> Story Boundary -> Flask response -> Browser or actor`

The Flask route is transport code. It selects the correct Boundary for the requested use case. The Boundary receives form or query input and sends it to its matching Controller. The Controller coordinates the use case. The Entity performs the domain operation. The Repository performs the SQL operation.

For ownership sensitive stories the Boundary passes the trusted session context to the Controller. The Controller obtains the account identifier from that context. Designer and customer identifiers are not accepted from editable form fields.

## Class count

The application keeps one Controller mapping for each of the 50 user stories. Login stories 11, 18, 35 and 47 share one LoginBoundary because they use the same login page and credential submission flow. Their role specific Controllers remain separate for user story traceability.

The main domain layer contains these Entity classes

1. UserProfile
2. UserAccount
3. Session
4. Company
5. IDP
6. Favourite
7. IDPCategory
8. ActivityEvent
9. ViewMetric
10. ShortlistMetric
11. ReportSummary
12. DailyReport
13. WeeklyReport
14. MonthlyReport

The persistence layer contains BaseRepository plus repositories for profiles, accounts, sessions, companies, categories, projects, favourites and activity events. Reversible actions stay inside the Controller for the original user story. Story 4 handles profile suspension and reactivation. Story 9 handles account suspension and reactivation. Story 32 handles save, unsave and saved state. Story 42 handles category suspension, reactivation and safe deletion. Profile deletion is Story 49 with its own Boundary and Controller. Read only browsing for authenticated non customer roles is Story 50 with its own Boundary and Controller.

## User story traceability

| Story | Boundary | Controller |
| --- | --- | --- |
| 1 | CreateUserProfileBoundary | CreateUserProfileController |
| 2 | ViewUserProfileBoundary | ViewUserProfileController |
| 3 | UpdateUserProfileBoundary | UpdateUserProfileController |
| 4 | SuspendUserProfileBoundary | SuspendUserProfileController |
| 5 | SearchUserProfileBoundary | SearchUserProfileController |
| 6 | CreateUserAccountBoundary | CreateUserAccountController |
| 7 | ViewUserAccountBoundary | ViewUserAccountController |
| 8 | UpdateUserAccountBoundary | UpdateUserAccountController |
| 9 | SuspendUserAccountBoundary | SuspendUserAccountController |
| 10 | SearchUserAccountBoundary | SearchUserAccountController |
| 11 | LoginBoundary | UserAdminLoginController |
| 12 | UserAdminLogoutBoundary | UserAdminLogoutController |
| 13 | CreateCompanyInformationBoundary | CreateCompanyInformationController |
| 14 | ViewCompanyInformationBoundary | ViewCompanyInformationController |
| 15 | UpdateCompanyInformationBoundary | UpdateCompanyInformationController |
| 16 | DeleteCompanyInformationBoundary | DeleteCompanyInformationController |
| 17 | SearchCompanyInformationBoundary | SearchCompanyInformationController |
| 18 | LoginBoundary | InteriorDesignerLoginController |
| 19 | InteriorDesignerLogoutBoundary | InteriorDesignerLogoutController |
| 20 | CreateCurrentIDPBoundary | CreateCurrentIDPController |
| 21 | ViewCurrentIDPBoundary | ViewCurrentIDPController |
| 22 | UpdateCurrentIDPBoundary | UpdateCurrentIDPController |
| 23 | DeleteCurrentIDPBoundary | DeleteCurrentIDPController |
| 24 | SearchCurrentIDPBoundary | SearchCurrentIDPController |
| 25 | CreatePastIDPBoundary | CreatePastIDPController |
| 26 | ViewPastIDPBoundary | ViewPastIDPController |
| 27 | UpdatePastIDPBoundary | UpdatePastIDPController |
| 28 | DeletePastIDPBoundary | DeletePastIDPController |
| 29 | SearchPastIDPBoundary | SearchPastIDPController |
| 30 | SearchAvailableIDPBoundary | SearchAvailableIDPController |
| 31 | ViewAvailableIDPBoundary | ViewAvailableIDPController |
| 32 | SaveIDPBoundary | SaveIDPController |
| 33 | SearchSavedIDPBoundary | SearchSavedIDPController |
| 34 | ViewSavedIDPBoundary | ViewSavedIDPController |
| 35 | LoginBoundary | CustomerLoginController |
| 36 | CustomerLogoutBoundary | CustomerLogoutController |
| 37 | ViewIDPViewsBoundary | ViewIDPViewsController |
| 38 | ViewIDPShortlistsBoundary | ViewIDPShortlistsController |
| 39 | CreateIDPCategoryBoundary | CreateIDPCategoryController |
| 40 | ViewIDPCategoryBoundary | ViewIDPCategoryController |
| 41 | UpdateIDPCategoryBoundary | UpdateIDPCategoryController |
| 42 | SuspendIDPCategoryBoundary | SuspendIDPCategoryController |
| 43 | SearchIDPCategoryBoundary | SearchIDPCategoryController |
| 44 | GenerateDailyReportBoundary | GenerateDailyReportController |
| 45 | GenerateWeeklyReportBoundary | GenerateWeeklyReportController |
| 46 | GenerateMonthlyReportBoundary | GenerateMonthlyReportController |
| 47 | LoginBoundary | PlatformManagerLoginController |
| 48 | PlatformManagerLogoutBoundary | PlatformManagerLogoutController |
| 49 | DeleteUserProfileBoundary | DeleteUserProfileController |
| 50 | BrowseIDPBoundary | BrowseIDPController |

## Login flow

The login page submits only username and password to LoginBoundary. LoginBoundary calls AuthenticationController. AuthenticationController asks UserAccount for the account, verifies that the account is active, asks UserAccount to verify the password, and asks UserProfile for the linked profile. The active profile role determines the role on the server. AuthenticationController then delegates the verified account and profile to the matching role specific login Controller. That Controller asks Session to create the authenticated session. The route stores the returned account identifier, role, display name and session identifier in the Flask session and redirects to the dashboard.

The browser does not submit a role. The role is trusted only after it is read from the linked UserProfile in the database.

## Logout flow

The logout Boundary passes the trusted session context to the matching logout Controller. The Controller obtains the current session identifier and asks Session to invalidate it. The Flask route then clears the local Flask session.

## Designer and customer ownership

Company, portfolio, favourite and metric Controllers read the authenticated account identifier from the trusted session context. Editable forms do not supply designer or customer ownership identifiers.

## Structural tests

`tests/test_story_controllers.py` verifies that all 50 stories have Controller mappings, all 50 story Controllers remain unique, the four login stories share LoginBoundary, and all non login story Boundaries remain unique.

## Diagram source

The `diagrams` folder contains one BCE diagram and one sequence diagram for each of the 50 user stories. Diagram class and method names are kept in sync with the implementation. Each story folder contains `BCE.mmd`, `Sequence.mmd` and a rendered Markdown preview in `README.md`.
