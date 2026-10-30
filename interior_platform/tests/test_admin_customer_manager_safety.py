from app.database import get_db
from werkzeug.security import generate_password_hash


def login_as(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def add_account(db, username, password, role, display_name=None):
    profile_id = db.execute(
        "SELECT profile_id FROM user_profiles WHERE role=? LIMIT 1",
        (role,),
    ).fetchone()[0]
    account_id = db.execute(
        "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
        (
            username,
            generate_password_hash(password),
            profile_id,
            display_name or username,
            f"{username}@test",
        ),
    ).lastrowid
    return account_id


def test_last_active_admin_account_cannot_suspend_itself(client, app):
    with app.app_context():
        db = get_db()
        admin_id = add_account(db, "onlyadmin", "pass", "User Admin")
        db.commit()
    login_as(client, "onlyadmin", "pass")
    response = client.post(
        f"/admin/accounts/{admin_id}/suspend",
        follow_redirects=True,
    )
    assert b"last active User Admin" in response.data
    with app.app_context():
        status = get_db().execute(
            "SELECT status FROM user_accounts WHERE account_id=?",
            (admin_id,),
        ).fetchone()[0]
    assert status == "Active"


def test_last_admin_profile_cannot_be_suspended(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "onlyadmin2", "pass", "User Admin")
        profile_id = db.execute(
            "SELECT profile_id FROM user_profiles WHERE role='User Admin' LIMIT 1"
        ).fetchone()[0]
        db.commit()
    login_as(client, "onlyadmin2", "pass")
    response = client.post(
        f"/admin/profiles/{profile_id}/suspend",
        follow_redirects=True,
    )
    assert b"no active User Admin" in response.data


def test_unused_profile_can_be_deleted(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "admin-delete-profile", "pass", "User Admin")
        profile_id = db.execute(
            "INSERT INTO user_profiles(name,description,role) VALUES(?,?,?)",
            ("Unused Customer", "", "Customer"),
        ).lastrowid
        db.commit()
    login_as(client, "admin-delete-profile", "pass")
    client.post(f"/admin/profiles/{profile_id}/delete", follow_redirects=True)
    with app.app_context():
        row = get_db().execute(
            "SELECT profile_id FROM user_profiles WHERE profile_id=?",
            (profile_id,),
        ).fetchone()
    assert row is None


def test_profile_in_use_cannot_be_deleted(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "admin-used-profile", "pass", "User Admin")
        customer_profile = db.execute(
            "SELECT profile_id FROM user_profiles WHERE role='Customer' LIMIT 1"
        ).fetchone()[0]
        db.commit()
    login_as(client, "admin-used-profile", "pass")
    response = client.post(
        f"/admin/profiles/{customer_profile}/delete",
        follow_redirects=True,
    )
    assert b"assigned to one or more user accounts" in response.data


def test_standard_profile_name_is_not_repeated_in_account_dropdown(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "admin-dropdown", "pass", "User Admin")
        db.commit()
    login_as(client, "admin-dropdown", "pass")
    response = client.get("/admin/accounts")
    assert b"Customer \xc2\xb7 Customer" not in response.data
    assert b">Customer<" in response.data


def test_saved_project_card_shows_saved_action(client, app):
    with app.app_context():
        db = get_db()
        designer_id = add_account(db, "designer-card", "pass", "Interior Designer")
        customer_id = db.execute(
            "SELECT account_id FROM user_accounts WHERE username='customer'"
        ).fetchone()[0]
        category_id = db.execute(
            "SELECT category_id FROM idp_categories LIMIT 1"
        ).fetchone()[0]
        project_id = db.execute(
            "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
            (designer_id, category_id, "Saved Card", "Test", "Current", 20, ""),
        ).lastrowid
        db.execute(
            "INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,datetime('now'))",
            (customer_id, project_id),
        )
        db.commit()
    login_as(client, "customer", "pass")
    response = client.get("/projects")
    assert b"Saved Card" in response.data
    assert b"Saved" in response.data
    assert f"/projects/{project_id}/unsave".encode() in response.data


def test_unused_category_can_be_deleted(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "manager-delete", "pass", "Platform Manager")
        category_id = db.execute(
            "INSERT INTO idp_categories(name,description) VALUES(?,?)",
            ("Unused Category", ""),
        ).lastrowid
        db.commit()
    login_as(client, "manager-delete", "pass")
    client.post(f"/manager/categories/{category_id}/delete", follow_redirects=True)
    with app.app_context():
        row = get_db().execute(
            "SELECT category_id FROM idp_categories WHERE category_id=?",
            (category_id,),
        ).fetchone()
    assert row is None


def test_category_in_use_cannot_be_deleted(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "manager-used", "pass", "Platform Manager")
        designer_id = add_account(db, "designer-used-category", "pass", "Interior Designer")
        category_id = db.execute(
            "SELECT category_id FROM idp_categories LIMIT 1"
        ).fetchone()[0]
        db.execute(
            "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
            (designer_id, category_id, "Uses Category", "Test", "Current", 10, ""),
        )
        db.commit()
    login_as(client, "manager-used", "pass")
    response = client.post(
        f"/manager/categories/{category_id}/delete",
        follow_redirects=True,
    )
    assert b"used by one or more projects" in response.data
