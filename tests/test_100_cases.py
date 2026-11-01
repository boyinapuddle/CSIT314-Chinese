import pytest
from werkzeug.security import generate_password_hash

from app.database import get_db
from app.entities import (
    UserProfile,
    UserAccount,
    Session,
    Company,
    IDP,
    Favourite,
    IDPCategory,
    DailyReport,
    WeeklyReport,
    MonthlyReport,
)
from app.controllers import (
    AuthenticationController,
    CustomerLoginController,
    BrowseIDPController,
    SaveIDPController,
    ViewAvailableIDPController,
    STORY_CONTROLLERS,
)
from app.boundaries import STORY_BOUNDARIES


def _profile_id(name):
    return get_db().execute(
        "SELECT profile_id FROM user_profiles WHERE name=?", (name,)
    ).fetchone()[0]


def _account_id(username="customer"):
    return get_db().execute(
        "SELECT account_id FROM user_accounts WHERE username=?", (username,)
    ).fetchone()[0]


def _create_account(username, role, password="pass", display_name=None, email=None):
    profile_id = get_db().execute(
        "SELECT profile_id FROM user_profiles WHERE role=? ORDER BY profile_id LIMIT 1",
        (role,),
    ).fetchone()[0]
    cur = get_db().execute(
        "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
        (
            username,
            generate_password_hash(password),
            profile_id,
            display_name or username.title(),
            email or f"{username}@test.local",
        ),
    )
    get_db().commit()
    return cur.lastrowid


def _category_id(name="Modern"):
    return get_db().execute(
        "SELECT category_id FROM idp_categories WHERE name=?", (name,)
    ).fetchone()[0]


def _create_project(designer_id, title="Project", status="Current", progress=50, visible=1, category_id=None, description="Design project"):
    category_id = category_id or _category_id()
    cur = get_db().execute(
        "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,visible,updated_at) VALUES(?,?,?,?,?,?,?,?,datetime('now'))",
        (designer_id, category_id, title, description, status, progress, "", visible),
    )
    get_db().commit()
    return cur.lastrowid


# User Profiles: TC001-TC015

def test_tc001_seed_contains_four_profiles(app):
    with app.app_context():
        assert len(UserProfile.search_profiles("")) == 4


def test_tc002_create_user_profile(app):
    with app.app_context():
        pid = UserProfile.create_profile("Home Owner", "Residential customer", "Customer")
        assert UserProfile.get_profile(pid)["name"] == "Home Owner"


def test_tc003_profile_description_is_trimmed(app):
    with app.app_context():
        pid = UserProfile.create_profile("VIP Customer", "  Priority profile  ", "Customer")
        assert UserProfile.get_profile(pid)["description"] == "Priority profile"


def test_tc004_profile_name_whitespace_is_normalized(app):
    with app.app_context():
        pid = UserProfile.create_profile("  Home   Owner  ", "", "Customer")
        assert UserProfile.get_profile(pid)["name"] == "Home Owner"


def test_tc005_blank_profile_name_is_rejected(app):
    with app.app_context(), pytest.raises(ValueError, match="required"):
        UserProfile.create_profile("   ", "", "Customer")


def test_tc006_invalid_profile_role_is_rejected(app):
    with app.app_context(), pytest.raises(ValueError, match="Invalid profile role"):
        UserProfile.create_profile("Invalid Role Profile", "", "Super User")


def test_tc007_duplicate_profile_is_case_insensitive(app):
    with app.app_context():
        UserProfile.create_profile("Home Owner", "", "Customer")
        with pytest.raises(ValueError, match="already exists"):
            UserProfile.create_profile("home owner", "", "Customer")


def test_tc008_duplicate_profile_ignores_repeated_spaces(app):
    with app.app_context():
        UserProfile.create_profile("Home Owner", "", "Customer")
        with pytest.raises(ValueError, match="already exists"):
            UserProfile.create_profile("home   owner", "", "Customer")


def test_tc009_view_existing_profile(app):
    with app.app_context():
        row = UserProfile.get_profile(_profile_id("Customer"))
        assert row["role"] == "Customer"


def test_tc010_search_profile_by_name(app):
    with app.app_context():
        rows = UserProfile.search_profiles("Interior")
        assert any(r["role"] == "Interior Designer" for r in rows)


def test_tc011_search_profile_by_description(app):
    with app.app_context():
        pid = UserProfile.create_profile("Premium Client", "Gold membership", "Customer")
        assert any(r["profile_id"] == pid for r in UserProfile.search_profiles("Gold"))


def test_tc012_blank_profile_search_returns_all(app):
    with app.app_context():
        assert len(UserProfile.search_profiles("")) == 4


def test_tc013_update_profile_name(app):
    with app.app_context():
        pid = UserProfile.create_profile("Old Name", "", "Customer")
        assert UserProfile.update_profile(pid, "New Name", "", "Customer") == 1
        assert UserProfile.get_profile(pid)["name"] == "New Name"


def test_tc014_update_profile_role(app):
    with app.app_context():
        pid = UserProfile.create_profile("Flexible", "", "Customer")
        UserProfile.update_profile(pid, "Flexible", "", "Interior Designer")
        assert UserProfile.get_profile(pid)["role"] == "Interior Designer"


def test_tc015_suspend_and_reactivate_profile(app):
    with app.app_context():
        pid = UserProfile.create_profile("Temporary", "", "Customer")
        assert UserProfile.suspend_profile(pid) == 1
        assert UserProfile.get_profile(pid)["status"] == "Suspended"
        assert UserProfile.reactivate_profile(pid) == 1
        assert UserProfile.get_profile(pid)["status"] == "Active"


# Accounts, Authentication and Sessions: TC016-TC040

def test_tc016_create_customer_account(app):
    with app.app_context():
        aid = UserAccount.create_account("alice", "secret", _profile_id("Customer"), "Alice", "alice@test.local")
        assert UserAccount.get_account(aid)["username"] == "alice"


def test_tc017_duplicate_username_is_rejected(app):
    with app.app_context():
        UserAccount.create_account("duplicate", "pass", _profile_id("Customer"), "One", "one@test.local")
        with pytest.raises(ValueError, match="already in use"):
            UserAccount.create_account("duplicate", "pass", _profile_id("Customer"), "Two", "two@test.local")


def test_tc018_suspended_profile_cannot_create_account(app):
    with app.app_context():
        pid = UserProfile.create_profile("Suspended Customer", "", "Customer")
        UserProfile.suspend_profile(pid)
        with pytest.raises(ValueError, match="active profile"):
            UserAccount.create_account("blocked", "pass", pid, "Blocked", "blocked@test.local")


def test_tc019_view_existing_account(app):
    with app.app_context():
        assert UserAccount.get_account(_account_id())["display_name"] == "Test Customer"


def test_tc020_search_account_by_username(app):
    with app.app_context():
        assert any(r["username"] == "customer" for r in UserAccount.search_accounts("customer"))


def test_tc021_search_account_by_display_name(app):
    with app.app_context():
        assert any(r["username"] == "customer" for r in UserAccount.search_accounts("Test Customer"))


def test_tc022_search_account_by_email(app):
    with app.app_context():
        assert any(r["username"] == "customer" for r in UserAccount.search_accounts("c@test"))


def test_tc023_update_account_display_name(app):
    with app.app_context():
        aid = _account_id()
        UserAccount.update_account(aid, "Updated Customer", "c@test", _profile_id("Customer"))
        assert UserAccount.get_account(aid)["display_name"] == "Updated Customer"


def test_tc024_update_account_email(app):
    with app.app_context():
        aid = _account_id()
        UserAccount.update_account(aid, "Test Customer", "new@test.local", _profile_id("Customer"))
        assert UserAccount.get_account(aid)["email"] == "new@test.local"


def test_tc025_update_account_profile(app):
    with app.app_context():
        aid = _account_id()
        UserAccount.update_account(aid, "Test Customer", "c@test", _profile_id("Interior Designer"))
        assert UserAccount.get_account(aid)["role"] == "Interior Designer"


def test_tc026_suspend_and_reactivate_account(app):
    with app.app_context():
        aid = _account_id()
        assert UserAccount.suspend_account(aid) == 1
        assert UserAccount.get_account(aid)["status"] == "Suspended"
        assert UserAccount.reactivate_account(aid) == 1
        assert UserAccount.get_account(aid)["status"] == "Active"


def test_tc027_suspend_missing_account_is_rejected(app):
    with app.app_context(), pytest.raises(ValueError, match="Account not found"):
        UserAccount.suspend_account(999999)


def test_tc028_reactivate_missing_account_is_rejected(app):
    with app.app_context(), pytest.raises(ValueError, match="Account not found"):
        UserAccount.reactivate_account(999999)


def test_tc029_verify_correct_password(app):
    with app.app_context():
        assert UserAccount.verify_password(UserAccount.find_by_username("customer"), "pass") is True


def test_tc030_verify_wrong_password(app):
    with app.app_context():
        assert UserAccount.verify_password(UserAccount.find_by_username("customer"), "wrong") is False


def test_tc031_verify_password_with_missing_account(app):
    with app.app_context():
        assert UserAccount.verify_password(None, "pass") is False


def test_tc032_access_state_returns_active_role(app):
    with app.app_context():
        state = UserAccount.access_state(_account_id())
        assert state["account_status"] == "Active" and state["role"] == "Customer"


def test_tc033_create_session_is_active(app):
    with app.app_context():
        sid = Session.create_session(_account_id(), "Customer")
        assert Session.is_active(sid) is True


def test_tc034_invalidate_session(app):
    with app.app_context():
        sid = Session.create_session(_account_id(), "Customer")
        assert Session.invalidate_session(sid) == 1
        assert Session.is_active(sid) is False


def test_tc035_authentication_rejects_unknown_username(app):
    with app.app_context():
        assert AuthenticationController().login("missing", "pass") is None


def test_tc036_customer_authentication_succeeds(app):
    with app.app_context():
        result = AuthenticationController().login("customer", "pass")
        assert result is not None and result[0]["role"] == "Customer"


def test_tc037_role_login_controller_rejects_wrong_profile_role(app):
    with app.app_context():
        account = UserAccount.find_by_username("customer")
        profile = UserProfile.get_profile(account["profile_id"])
        assert CustomerLoginController().complete_login(account, {**dict(profile), "role": "User Admin"}) is None


def test_tc038_last_active_admin_account_cannot_be_suspended(app):
    with app.app_context():
        aid = _create_account("onlyadmin", "User Admin")
        with pytest.raises(ValueError, match="last active User Admin"):
            UserAccount.suspend_account(aid)


def test_tc039_last_active_admin_cannot_move_to_non_admin_profile(app):
    with app.app_context():
        aid = _create_account("onlyadmin", "User Admin")
        with pytest.raises(ValueError, match="last active User Admin"):
            UserAccount.update_account(aid, "Only Admin", "a@test.local", _profile_id("Customer"))


def test_tc040_admin_can_be_suspended_when_another_active_admin_exists(app):
    with app.app_context():
        first = _create_account("admin1", "User Admin")
        _create_account("admin2", "User Admin")
        assert UserAccount.suspend_account(first) == 1


# Company Information: TC041-TC050

def test_tc041_create_company(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        cid = Company.create_company(did, {"name": "Studio One"})
        assert cid > 0


def test_tc042_view_company(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Studio One"})
        assert Company.get_company(did)["name"] == "Studio One"


def test_tc043_company_fields_are_trimmed(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "  Studio One  ", "address": "  Bedok  "})
        row = Company.get_company(did)
        assert row["name"] == "Studio One" and row["address"] == "Bedok"


def test_tc044_update_company_name(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Old Studio"})
        assert Company.update_company(did, {"name": "New Studio"}) == 1
        assert Company.get_company(did)["name"] == "New Studio"


def test_tc045_update_company_contact_fields(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Studio"})
        Company.update_company(did, {"name": "Studio", "phone": "1234", "email": "studio@test.local", "website": "example.test"})
        row = Company.get_company(did)
        assert row["phone"] == "1234" and row["email"] == "studio@test.local"


def test_tc046_search_company_by_name(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Azure Interiors"})
        assert len(Company.search_company(did, "Azure")) == 1


def test_tc047_search_company_by_description(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Studio", "description": "Luxury residential design"})
        assert len(Company.search_company(did, "Luxury")) == 1


def test_tc048_search_company_by_address(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Studio", "address": "Orchard Road"})
        assert len(Company.search_company(did, "Orchard")) == 1


def test_tc049_company_search_is_restricted_to_owner(app):
    with app.app_context():
        d1 = _create_account("designer1", "Interior Designer")
        d2 = _create_account("designer2", "Interior Designer")
        Company.create_company(d1, {"name": "Private Studio"})
        assert Company.search_company(d2, "Private") == []


def test_tc050_delete_company(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Company.create_company(did, {"name": "Studio"})
        assert Company.delete_company(did) == 1
        assert Company.get_company(did) is None


# Projects and Browsing: TC051-TC070

def test_tc051_create_current_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = IDP.create_project(did, {"category_id": _category_id(), "title": "Living Room", "description": "Modern living", "progress": 40}, "Current")
        assert IDP.get_available_project(pid)["project_status"] == "Current"


def test_tc052_create_past_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = IDP.create_project(did, {"category_id": _category_id(), "title": "Completed Home", "description": "Completed", "progress": 100}, "Past")
        assert IDP.get_available_project(pid)["project_status"] == "Past"


def test_tc053_project_title_is_trimmed(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = IDP.create_project(did, {"category_id": _category_id(), "title": "  Bedroom  ", "description": "x", "progress": 20}, "Current")
        assert IDP.get_available_project(pid)["title"] == "Bedroom"


def test_tc054_project_description_is_trimmed(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = IDP.create_project(did, {"category_id": _category_id(), "title": "Bedroom", "description": "  Calm design  ", "progress": 20}, "Current")
        assert IDP.get_available_project(pid)["description"] == "Calm design"


def test_tc055_project_progress_defaults_to_zero(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = IDP.create_project(did, {"category_id": _category_id(), "title": "New", "description": "New"}, "Current")
        assert IDP.get_available_project(pid)["progress"] == 0


def test_tc056_view_owned_current_projects(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        _create_project(did, "Current A", "Current")
        _create_project(did, "Past A", "Past")
        assert [r["title"] for r in IDP.get_owned_projects(did, "Current")] == ["Current A"]


def test_tc057_view_owned_past_projects(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        _create_project(did, "Current A", "Current")
        _create_project(did, "Past A", "Past")
        assert [r["title"] for r in IDP.get_owned_projects(did, "Past")] == ["Past A"]


def test_tc058_search_owned_project_by_title(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        _create_project(did, "Coastal Kitchen", "Current")
        assert len(IDP.search_owned_projects(did, "Current", "Coastal")) == 1


def test_tc059_search_owned_project_by_description(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        _create_project(did, "Kitchen", "Current", description="Warm timber finish")
        assert len(IDP.search_owned_projects(did, "Current", "timber")) == 1


def test_tc060_owned_project_search_does_not_return_other_designers(app):
    with app.app_context():
        d1 = _create_account("designer1", "Interior Designer")
        d2 = _create_account("designer2", "Interior Designer")
        _create_project(d1, "Private Project", "Current")
        assert IDP.search_owned_projects(d2, "Current", "Private") == []


def test_tc061_update_owned_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Old", "Current")
        changed = IDP.update_owned_project(pid, did, {"category_id": _category_id(), "title": "New", "description": "Updated", "progress": 75}, "Current")
        assert changed == 1 and IDP.get_available_project(pid)["title"] == "New"


def test_tc062_other_designer_cannot_update_project(app):
    with app.app_context():
        d1 = _create_account("designer1", "Interior Designer")
        d2 = _create_account("designer2", "Interior Designer")
        pid = _create_project(d1, "Owned", "Current")
        changed = IDP.update_owned_project(pid, d2, {"category_id": _category_id(), "title": "Hack", "description": "x", "progress": 10}, "Current")
        assert changed == 0


def test_tc063_wrong_status_cannot_update_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Past", "Past")
        changed = IDP.update_owned_project(pid, did, {"category_id": _category_id(), "title": "Hack", "description": "x", "progress": 10}, "Current")
        assert changed == 0


def test_tc064_delete_owned_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Delete Me", "Current")
        assert IDP.delete_owned_project(pid, did, "Current") == 1


def test_tc065_wrong_status_cannot_delete_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Keep Me", "Past")
        assert IDP.delete_owned_project(pid, did, "Current") == 0


def test_tc066_available_search_returns_visible_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Visible Inspiration", "Current")
        assert any(r["project_id"] == pid for r in IDP.search_available_projects("Visible"))


def test_tc067_available_search_excludes_hidden_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Hidden Inspiration", "Current", visible=0)
        assert all(r["project_id"] != pid for r in IDP.search_available_projects("Hidden"))


def test_tc068_available_search_excludes_suspended_category(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Suspended Category Project", "Current")
        IDPCategory.suspend_category(_category_id())
        assert all(r["project_id"] != pid for r in IDP.search_available_projects("Suspended"))


def test_tc069_get_available_project_returns_none_for_hidden_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Hidden", "Current", visible=0)
        assert IDP.get_available_project(pid) is None


def test_tc070_non_customer_browse_controller_can_search(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        _create_project(did, "Browse Me", "Current")
        rows = BrowseIDPController().search({"account_id": did, "role": "Interior Designer"}, "Browse")
        assert len(rows) == 1


# Favourites, Views and Analytics: TC071-TC085

def test_tc071_customer_can_save_available_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Favourite", "Current")
        assert Favourite.save_project(_account_id(), pid) is True


def test_tc072_duplicate_favourite_is_not_created(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Favourite", "Current")
        assert Favourite.save_project(_account_id(), pid) is True
        assert Favourite.save_project(_account_id(), pid) is False


def test_tc073_is_saved_returns_true_after_save(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Favourite", "Current")
        Favourite.save_project(_account_id(), pid)
        assert Favourite.is_saved(_account_id(), pid) is True


def test_tc074_remove_saved_project(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Favourite", "Current")
        Favourite.save_project(_account_id(), pid)
        assert Favourite.remove_project(_account_id(), pid) is True
        assert Favourite.is_saved(_account_id(), pid) is False


def test_tc075_remove_missing_favourite_returns_false(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Not Saved", "Current")
        assert Favourite.remove_project(_account_id(), pid) is False


def test_tc076_search_saved_project_by_title(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Scandinavian Loft", "Current")
        Favourite.save_project(_account_id(), pid)
        assert len(Favourite.search_saved_projects(_account_id(), "Scandinavian")) == 1


def test_tc077_search_saved_project_by_category(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Loft", "Current")
        Favourite.save_project(_account_id(), pid)
        assert len(Favourite.search_saved_projects(_account_id(), "Modern")) == 1


def test_tc078_view_all_saved_projects(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        Favourite.save_project(_account_id(), _create_project(did, "One", "Current"))
        Favourite.save_project(_account_id(), _create_project(did, "Two", "Current"))
        assert len(Favourite.view_saved_projects(_account_id())) == 2


def test_tc079_hidden_project_cannot_be_saved(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Hidden", "Current", visible=0)
        assert Favourite.save_project(_account_id(), pid) is False


def test_tc080_project_in_suspended_category_cannot_be_saved(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Unavailable", "Current")
        IDPCategory.suspend_category(_category_id())
        assert Favourite.save_project(_account_id(), pid) is False


def test_tc081_customer_save_controller_accepts_customer(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Save Controller", "Current")
        assert SaveIDPController().save({"account_id": _account_id(), "role": "Customer"}, pid) is True


def test_tc082_save_controller_rejects_non_customer(app):
    with app.app_context(), pytest.raises(PermissionError):
        SaveIDPController().save({"account_id": 123, "role": "User Admin"}, 1)


def test_tc083_customer_project_view_increments_view_count(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Viewed", "Current")
        ViewAvailableIDPController().view({"account_id": _account_id(), "role": "Customer"}, pid)
        row = IDP.get_available_project(pid)
        assert row["views"] == 1


def test_tc084_saving_project_increments_shortlist_count(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Shortlisted", "Current")
        Favourite.save_project(_account_id(), pid)
        assert IDP.get_available_project(pid)["shortlists"] == 1


def test_tc085_unsaving_project_reduces_shortlist_count(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        pid = _create_project(did, "Shortlisted", "Current")
        Favourite.save_project(_account_id(), pid)
        Favourite.remove_project(_account_id(), pid)
        assert IDP.get_available_project(pid)["shortlists"] == 0


# Categories: TC086-TC096

def test_tc086_create_category(app):
    with app.app_context():
        cid = IDPCategory.create_category("Industrial", "Raw finishes")
        assert IDPCategory.get_category(cid)["name"] == "Industrial"


def test_tc087_category_name_whitespace_is_normalized(app):
    with app.app_context():
        cid = IDPCategory.create_category("  Japandi   Style  ", "")
        assert IDPCategory.get_category(cid)["name"] == "Japandi Style"


def test_tc088_duplicate_category_is_case_insensitive(app):
    with app.app_context(), pytest.raises(ValueError, match="already exists"):
        IDPCategory.create_category("modern", "Duplicate")


def test_tc089_view_category(app):
    with app.app_context():
        assert IDPCategory.get_category(_category_id())["description"] == "Modern spaces"


def test_tc090_view_all_categories(app):
    with app.app_context():
        IDPCategory.create_category("Classic", "")
        assert len(IDPCategory.get_categories()) == 2


def test_tc091_update_category(app):
    with app.app_context():
        cid = IDPCategory.create_category("Old Category", "")
        assert IDPCategory.update_category(cid, "New Category", "Updated") == 1
        assert IDPCategory.get_category(cid)["name"] == "New Category"


def test_tc092_search_category_by_name(app):
    with app.app_context():
        IDPCategory.create_category("Minimalist", "")
        assert len(IDPCategory.search_categories("Minimal")) == 1


def test_tc093_suspended_category_is_excluded_from_active_list(app):
    with app.app_context():
        cid = IDPCategory.create_category("Temporary", "")
        IDPCategory.suspend_category(cid)
        assert all(r["category_id"] != cid for r in IDPCategory.get_categories(True))


def test_tc094_reactivate_category(app):
    with app.app_context():
        cid = IDPCategory.create_category("Temporary", "")
        IDPCategory.suspend_category(cid)
        assert IDPCategory.reactivate_category(cid) == 1
        assert IDPCategory.get_category(cid)["status"] == "Active"


def test_tc095_delete_unused_category(app):
    with app.app_context():
        cid = IDPCategory.create_category("Unused", "")
        assert IDPCategory.delete_category(cid) == 1
        assert IDPCategory.get_category(cid) is None


def test_tc096_category_in_use_cannot_be_deleted(app):
    with app.app_context():
        did = _create_account("designer", "Interior Designer")
        cid = IDPCategory.create_category("Used", "")
        _create_project(did, "Uses Category", "Current", category_id=cid)
        with pytest.raises(ValueError, match="used by one or more projects"):
            IDPCategory.delete_category(cid)


# Reports and Architecture: TC097-TC100

def test_tc097_daily_report_has_expected_fields(app):
    with app.app_context():
        report = DailyReport.generate()
        assert {"period", "from", "to", "selected", "users", "projects", "views", "shortlists"} <= set(report)
        assert report["period"] == "Daily"


def test_tc098_weekly_report_has_weekly_period(app):
    with app.app_context():
        assert WeeklyReport.generate()["period"] == "Weekly"


def test_tc099_monthly_report_has_monthly_period(app):
    with app.app_context():
        assert MonthlyReport.generate()["period"] == "Monthly"


def test_tc100_all_fifty_stories_have_controller_and_boundary_mappings():
    assert set(STORY_CONTROLLERS) == set(range(1, 51))
    assert set(STORY_BOUNDARIES) == set(range(1, 51))
