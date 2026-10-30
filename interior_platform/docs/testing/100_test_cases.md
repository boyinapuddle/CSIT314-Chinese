# Automated Test Case Register

This register maps the 100 additional automated pytest cases in `tests/test_100_cases.py` to report-friendly test case IDs.

Run only these 100 cases with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_100_cases.py -v
```

Run the complete regression suite with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

| Test ID | Area | Test objective | Automated function |
|---|---|---|---|
| TC001 | User Profiles | Seed contains four profiles | `test_tc001_seed_contains_four_profiles` |
| TC002 | User Profiles | Create user profile | `test_tc002_create_user_profile` |
| TC003 | User Profiles | Profile description is trimmed | `test_tc003_profile_description_is_trimmed` |
| TC004 | User Profiles | Profile name whitespace is normalized | `test_tc004_profile_name_whitespace_is_normalized` |
| TC005 | User Profiles | Blank profile name is rejected | `test_tc005_blank_profile_name_is_rejected` |
| TC006 | User Profiles | Invalid profile role is rejected | `test_tc006_invalid_profile_role_is_rejected` |
| TC007 | User Profiles | Duplicate profile is case insensitive | `test_tc007_duplicate_profile_is_case_insensitive` |
| TC008 | User Profiles | Duplicate profile ignores repeated spaces | `test_tc008_duplicate_profile_ignores_repeated_spaces` |
| TC009 | User Profiles | View existing profile | `test_tc009_view_existing_profile` |
| TC010 | User Profiles | Search profile by name | `test_tc010_search_profile_by_name` |
| TC011 | User Profiles | Search profile by description | `test_tc011_search_profile_by_description` |
| TC012 | User Profiles | Blank profile search returns all | `test_tc012_blank_profile_search_returns_all` |
| TC013 | User Profiles | Update profile name | `test_tc013_update_profile_name` |
| TC014 | User Profiles | Update profile role | `test_tc014_update_profile_role` |
| TC015 | User Profiles | Suspend and reactivate profile | `test_tc015_suspend_and_reactivate_profile` |
| TC016 | Accounts, Authentication and Sessions | Create customer account | `test_tc016_create_customer_account` |
| TC017 | Accounts, Authentication and Sessions | Duplicate username is rejected | `test_tc017_duplicate_username_is_rejected` |
| TC018 | Accounts, Authentication and Sessions | Suspended profile cannot create account | `test_tc018_suspended_profile_cannot_create_account` |
| TC019 | Accounts, Authentication and Sessions | View existing account | `test_tc019_view_existing_account` |
| TC020 | Accounts, Authentication and Sessions | Search account by username | `test_tc020_search_account_by_username` |
| TC021 | Accounts, Authentication and Sessions | Search account by display name | `test_tc021_search_account_by_display_name` |
| TC022 | Accounts, Authentication and Sessions | Search account by email | `test_tc022_search_account_by_email` |
| TC023 | Accounts, Authentication and Sessions | Update account display name | `test_tc023_update_account_display_name` |
| TC024 | Accounts, Authentication and Sessions | Update account email | `test_tc024_update_account_email` |
| TC025 | Accounts, Authentication and Sessions | Update account profile | `test_tc025_update_account_profile` |
| TC026 | Accounts, Authentication and Sessions | Suspend and reactivate account | `test_tc026_suspend_and_reactivate_account` |
| TC027 | Accounts, Authentication and Sessions | Suspend missing account is rejected | `test_tc027_suspend_missing_account_is_rejected` |
| TC028 | Accounts, Authentication and Sessions | Reactivate missing account is rejected | `test_tc028_reactivate_missing_account_is_rejected` |
| TC029 | Accounts, Authentication and Sessions | Verify correct password | `test_tc029_verify_correct_password` |
| TC030 | Accounts, Authentication and Sessions | Verify wrong password | `test_tc030_verify_wrong_password` |
| TC031 | Accounts, Authentication and Sessions | Verify password with missing account | `test_tc031_verify_password_with_missing_account` |
| TC032 | Accounts, Authentication and Sessions | Access state returns active role | `test_tc032_access_state_returns_active_role` |
| TC033 | Accounts, Authentication and Sessions | Create session is active | `test_tc033_create_session_is_active` |
| TC034 | Accounts, Authentication and Sessions | Invalidate session | `test_tc034_invalidate_session` |
| TC035 | Accounts, Authentication and Sessions | Authentication rejects unknown username | `test_tc035_authentication_rejects_unknown_username` |
| TC036 | Accounts, Authentication and Sessions | Customer authentication succeeds | `test_tc036_customer_authentication_succeeds` |
| TC037 | Accounts, Authentication and Sessions | Role login controller rejects wrong profile role | `test_tc037_role_login_controller_rejects_wrong_profile_role` |
| TC038 | Accounts, Authentication and Sessions | Last active admin account cannot be suspended | `test_tc038_last_active_admin_account_cannot_be_suspended` |
| TC039 | Accounts, Authentication and Sessions | Last active admin cannot move to non admin profile | `test_tc039_last_active_admin_cannot_move_to_non_admin_profile` |
| TC040 | Accounts, Authentication and Sessions | Admin can be suspended when another active admin exists | `test_tc040_admin_can_be_suspended_when_another_active_admin_exists` |
| TC041 | Company Information | Create company | `test_tc041_create_company` |
| TC042 | Company Information | View company | `test_tc042_view_company` |
| TC043 | Company Information | Company fields are trimmed | `test_tc043_company_fields_are_trimmed` |
| TC044 | Company Information | Update company name | `test_tc044_update_company_name` |
| TC045 | Company Information | Update company contact fields | `test_tc045_update_company_contact_fields` |
| TC046 | Company Information | Search company by name | `test_tc046_search_company_by_name` |
| TC047 | Company Information | Search company by description | `test_tc047_search_company_by_description` |
| TC048 | Company Information | Search company by address | `test_tc048_search_company_by_address` |
| TC049 | Company Information | Company search is restricted to owner | `test_tc049_company_search_is_restricted_to_owner` |
| TC050 | Company Information | Delete company | `test_tc050_delete_company` |
| TC051 | Projects and Browsing | Create current project | `test_tc051_create_current_project` |
| TC052 | Projects and Browsing | Create past project | `test_tc052_create_past_project` |
| TC053 | Projects and Browsing | Project title is trimmed | `test_tc053_project_title_is_trimmed` |
| TC054 | Projects and Browsing | Project description is trimmed | `test_tc054_project_description_is_trimmed` |
| TC055 | Projects and Browsing | Project progress defaults to zero | `test_tc055_project_progress_defaults_to_zero` |
| TC056 | Projects and Browsing | View owned current projects | `test_tc056_view_owned_current_projects` |
| TC057 | Projects and Browsing | View owned past projects | `test_tc057_view_owned_past_projects` |
| TC058 | Projects and Browsing | Search owned project by title | `test_tc058_search_owned_project_by_title` |
| TC059 | Projects and Browsing | Search owned project by description | `test_tc059_search_owned_project_by_description` |
| TC060 | Projects and Browsing | Owned project search does not return other designers | `test_tc060_owned_project_search_does_not_return_other_designers` |
| TC061 | Projects and Browsing | Update owned project | `test_tc061_update_owned_project` |
| TC062 | Projects and Browsing | Other designer cannot update project | `test_tc062_other_designer_cannot_update_project` |
| TC063 | Projects and Browsing | Wrong status cannot update project | `test_tc063_wrong_status_cannot_update_project` |
| TC064 | Projects and Browsing | Delete owned project | `test_tc064_delete_owned_project` |
| TC065 | Projects and Browsing | Wrong status cannot delete project | `test_tc065_wrong_status_cannot_delete_project` |
| TC066 | Projects and Browsing | Available search returns visible project | `test_tc066_available_search_returns_visible_project` |
| TC067 | Projects and Browsing | Available search excludes hidden project | `test_tc067_available_search_excludes_hidden_project` |
| TC068 | Projects and Browsing | Available search excludes suspended category | `test_tc068_available_search_excludes_suspended_category` |
| TC069 | Projects and Browsing | Get available project returns none for hidden project | `test_tc069_get_available_project_returns_none_for_hidden_project` |
| TC070 | Projects and Browsing | Non customer browse controller can search | `test_tc070_non_customer_browse_controller_can_search` |
| TC071 | Favourites, Views and Analytics | Customer can save available project | `test_tc071_customer_can_save_available_project` |
| TC072 | Favourites, Views and Analytics | Duplicate favourite is not created | `test_tc072_duplicate_favourite_is_not_created` |
| TC073 | Favourites, Views and Analytics | Is saved returns true after save | `test_tc073_is_saved_returns_true_after_save` |
| TC074 | Favourites, Views and Analytics | Remove saved project | `test_tc074_remove_saved_project` |
| TC075 | Favourites, Views and Analytics | Remove missing favourite returns false | `test_tc075_remove_missing_favourite_returns_false` |
| TC076 | Favourites, Views and Analytics | Search saved project by title | `test_tc076_search_saved_project_by_title` |
| TC077 | Favourites, Views and Analytics | Search saved project by category | `test_tc077_search_saved_project_by_category` |
| TC078 | Favourites, Views and Analytics | View all saved projects | `test_tc078_view_all_saved_projects` |
| TC079 | Favourites, Views and Analytics | Hidden project cannot be saved | `test_tc079_hidden_project_cannot_be_saved` |
| TC080 | Favourites, Views and Analytics | Project in suspended category cannot be saved | `test_tc080_project_in_suspended_category_cannot_be_saved` |
| TC081 | Favourites, Views and Analytics | Customer save controller accepts customer | `test_tc081_customer_save_controller_accepts_customer` |
| TC082 | Favourites, Views and Analytics | Save controller rejects non customer | `test_tc082_save_controller_rejects_non_customer` |
| TC083 | Favourites, Views and Analytics | Customer project view increments view count | `test_tc083_customer_project_view_increments_view_count` |
| TC084 | Favourites, Views and Analytics | Saving project increments shortlist count | `test_tc084_saving_project_increments_shortlist_count` |
| TC085 | Favourites, Views and Analytics | Unsaving project reduces shortlist count | `test_tc085_unsaving_project_reduces_shortlist_count` |
| TC086 | IDP Categories | Create category | `test_tc086_create_category` |
| TC087 | IDP Categories | Category name whitespace is normalized | `test_tc087_category_name_whitespace_is_normalized` |
| TC088 | IDP Categories | Duplicate category is case insensitive | `test_tc088_duplicate_category_is_case_insensitive` |
| TC089 | IDP Categories | View category | `test_tc089_view_category` |
| TC090 | IDP Categories | View all categories | `test_tc090_view_all_categories` |
| TC091 | IDP Categories | Update category | `test_tc091_update_category` |
| TC092 | IDP Categories | Search category by name | `test_tc092_search_category_by_name` |
| TC093 | IDP Categories | Suspended category is excluded from active list | `test_tc093_suspended_category_is_excluded_from_active_list` |
| TC094 | IDP Categories | Reactivate category | `test_tc094_reactivate_category` |
| TC095 | IDP Categories | Delete unused category | `test_tc095_delete_unused_category` |
| TC096 | IDP Categories | Category in use cannot be deleted | `test_tc096_category_in_use_cannot_be_deleted` |
| TC097 | Reports and Architecture | Daily report has expected fields | `test_tc097_daily_report_has_expected_fields` |
| TC098 | Reports and Architecture | Weekly report has weekly period | `test_tc098_weekly_report_has_weekly_period` |
| TC099 | Reports and Architecture | Monthly report has monthly period | `test_tc099_monthly_report_has_monthly_period` |
| TC100 | Reports and Architecture | All fifty stories have controller and boundary mappings | `test_tc100_all_fifty_stories_have_controller_and_boundary_mappings` |
