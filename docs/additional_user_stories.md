# Additional User Stories

## User Story 49

**As a User Admin, I want to delete an unused user profile so that obsolete profiles can be removed from the platform.**

| Field | Detail |
| --- | --- |
| Actor | User Admin |
| Goal | Permanently remove an obsolete user profile that is not assigned to any account. |
| Trigger | The User Admin selects Delete for a user profile. |
| Preconditions | The User Admin has an authenticated active User Admin session. The profile exists and is not assigned to any user account. |
| Postconditions | On success, the profile is deleted. If the profile is still assigned to an account, nothing is deleted and a validation message is displayed. |
| Main flow | 1. The User Admin selects Delete. 2. `DeleteUserProfileBoundary` sends the profile ID to `DeleteUserProfileController`. 3. The controller asks `UserProfile` to delete the profile. 4. `UserProfile` checks whether accounts still reference the profile. 5. If none do, the profile is deleted. 6. The boundary displays the result. |
| Alternative flow | A1. The profile does not exist. Display an error and do not delete anything. A2. One or more accounts use the profile. Reject deletion and instruct the admin to reassign those accounts first. |

## User Story 50

**As an authenticated non customer user, I want to browse available Interior Design Projects so that I can view project information without performing customer favourite actions.**

Authenticated non customer users are User Admin, Interior Designer and Platform Manager accounts.

| Field | Detail |
| --- | --- |
| Actor | Authenticated non customer user |
| Goal | Search and view available IDPs in read only mode. |
| Trigger | The authenticated user opens the Projects page, searches, or selects a project. |
| Preconditions | The user has an authenticated active session and the role is User Admin, Interior Designer or Platform Manager. |
| Postconditions | Matching available projects or selected project details are displayed. No favourite record is created or removed and no customer interest view is recorded. |
| Main flow | 1. The user opens Projects or submits a keyword. 2. `BrowseIDPBoundary` calls `BrowseIDPController`. 3. The controller asks `IDP` for available projects or project details. 4. The result is returned to the boundary for display. |
| Alternative flow | A1. No project matches the search. Display an empty result message. A2. The selected project is unavailable. Display a not found response. A3. A non customer attempts a favourite action. Access is rejected. |
