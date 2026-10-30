from app.database import get_db
from werkzeug.security import generate_password_hash


def login_as(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_duplicate_profile_name_returns_validation_message(client, app):
    with app.app_context():
        db = get_db()
        admin_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='User Admin'").fetchone()[0]
        db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("admin2", generate_password_hash("pass"), admin_profile, "Admin", "admin@test"),
        )
        db.commit()
    login_as(client, "admin2", "pass")
    response = client.post(
        "/admin/profiles",
        data={"name": "Customer", "description": "Duplicate", "role": "Customer"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_custom_profile_role_allows_new_account_to_login(client, app):
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            "INSERT INTO user_profiles(name,description,role) VALUES(?,?,?)",
            ("Home Owner", "Customer access", "Customer"),
        )
        profile_id = cursor.lastrowid
        db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("newcustomer", generate_password_hash("newpass"), profile_id, "New Customer", "new@test"),
        )
        db.commit()
    response = login_as(client, "newcustomer", "newpass")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_profile_can_be_reactivated(client, app):
    with app.app_context():
        db = get_db()
        admin_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='User Admin'").fetchone()[0]
        customer_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='Customer'").fetchone()[0]
        db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("admin3", generate_password_hash("pass"), admin_profile, "Admin", "admin3@test"),
        )
        db.commit()
    login_as(client, "admin3", "pass")
    client.post(f"/admin/profiles/{customer_profile}/suspend")
    client.post(f"/admin/profiles/{customer_profile}/reactivate")
    with app.app_context():
        status = get_db().execute(
            "SELECT status FROM user_profiles WHERE profile_id=?",
            (customer_profile,),
        ).fetchone()[0]
    assert status == "Active"


def test_unsave_reduces_shortlist_count(client, app):
    with app.app_context():
        db = get_db()
        designer_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='Interior Designer'").fetchone()[0]
        customer_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='Customer'").fetchone()[0]
        designer_id = db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("designer2", generate_password_hash("pass"), designer_profile, "Designer", "designer2@test"),
        ).lastrowid
        customer_id = db.execute("SELECT account_id FROM user_accounts WHERE username='customer'").fetchone()[0]
        category_id = db.execute("SELECT category_id FROM idp_categories LIMIT 1").fetchone()[0]
        project_id = db.execute(
            "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
            (designer_id, category_id, "Saved Project", "Test", "Current", 10, ""),
        ).lastrowid
        db.execute(
            "INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,datetime('now'))",
            (customer_id, project_id),
        )
        db.commit()
    login_as(client, "customer", "pass")
    client.post(f"/projects/{project_id}/unsave")
    with app.app_context():
        count = get_db().execute(
            "SELECT COUNT(*) FROM favourites WHERE project_id=?",
            (project_id,),
        ).fetchone()[0]
    assert count == 0


def test_category_can_be_reactivated(client, app):
    with app.app_context():
        db = get_db()
        manager_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='Platform Manager'").fetchone()[0]
        manager_id = db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("manager2", generate_password_hash("pass"), manager_profile, "Manager", "manager@test"),
        ).lastrowid
        category_id = db.execute("SELECT category_id FROM idp_categories LIMIT 1").fetchone()[0]
        db.commit()
    login_as(client, "manager2", "pass")
    client.post(f"/manager/categories/{category_id}/suspend")
    client.post(f"/manager/categories/{category_id}/reactivate")
    with app.app_context():
        status = get_db().execute(
            "SELECT status FROM idp_categories WHERE category_id=?",
            (category_id,),
        ).fetchone()[0]
    assert status == "Active"


def test_account_can_be_reactivated(client, app):
    with app.app_context():
        db = get_db()
        admin_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='User Admin'").fetchone()[0]
        customer_profile = db.execute("SELECT profile_id FROM user_profiles WHERE role='Customer'").fetchone()[0]
        db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            ("admin-reactivate-account", generate_password_hash("pass"), admin_profile, "Admin", "admin-reactivate@test"),
        )
        account_id = db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email,status) VALUES(?,?,?,?,?,?)",
            ("suspended-customer", generate_password_hash("pass"), customer_profile, "Suspended Customer", "suspended@test", "Suspended"),
        ).lastrowid
        db.commit()
    login_as(client, "admin-reactivate-account", "pass")
    response = client.post(f"/admin/accounts/{account_id}/reactivate", follow_redirects=True)
    assert b"Account reactivated" in response.data
    with app.app_context():
        status = get_db().execute(
            "SELECT status FROM user_accounts WHERE account_id=?",
            (account_id,),
        ).fetchone()[0]
    assert status == "Active"
