from app.database import get_db
from werkzeug.security import generate_password_hash


def add_account(db, username, password, role):
    profile_id = db.execute(
        "SELECT profile_id FROM user_profiles WHERE role=? LIMIT 1",
        (role,),
    ).fetchone()[0]
    return db.execute(
        "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
        (username, generate_password_hash(password), profile_id, username, f"{username}@test"),
    ).lastrowid


def login_as(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def add_project(db):
    designer_id = add_account(db, "browse-designer", "pass", "Interior Designer")
    category_id = db.execute("SELECT category_id FROM idp_categories LIMIT 1").fetchone()[0]
    project_id = db.execute(
        "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,datetime('now'))",
        (designer_id, category_id, "Shared Browse Project", "Visible to authenticated roles", "Current", 40, ""),
    ).lastrowid
    return project_id


def test_admin_can_browse_projects_without_customer_actions(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "browse-admin", "pass", "User Admin")
        project_id = add_project(db)
        db.commit()
    login_as(client, "browse-admin", "pass")
    response = client.get("/projects")
    assert response.status_code == 200
    assert b"Shared Browse Project" in response.data
    assert b"Save" not in response.data
    detail = client.get(f"/projects/{project_id}")
    assert detail.status_code == 200
    assert b"Save to favourites" not in detail.data


def test_admin_project_view_does_not_count_as_customer_interest(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "view-admin", "pass", "User Admin")
        project_id = add_project(db)
        db.commit()
    login_as(client, "view-admin", "pass")
    client.get(f"/projects/{project_id}")
    with app.app_context():
        count = get_db().execute(
            "SELECT COUNT(*) FROM project_views WHERE project_id=?",
            (project_id,),
        ).fetchone()[0]
    assert count == 0


def test_customer_project_view_still_counts(client, app):
    with app.app_context():
        db = get_db()
        project_id = add_project(db)
        db.commit()
    login_as(client, "customer", "pass")
    client.get(f"/projects/{project_id}")
    with app.app_context():
        count = get_db().execute(
            "SELECT COUNT(*) FROM project_views WHERE project_id=?",
            (project_id,),
        ).fetchone()[0]
    assert count == 1


def test_non_customer_cannot_post_save(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "save-admin", "pass", "User Admin")
        project_id = add_project(db)
        db.commit()
    login_as(client, "save-admin", "pass")
    response = client.post(f"/projects/{project_id}/save")
    assert response.status_code == 403


def test_logged_in_user_visiting_login_is_redirected_to_dashboard(client, app):
    with app.app_context():
        db = get_db()
        add_account(db, "login-admin", "pass", "User Admin")
        db.commit()
    login_as(client, "login-admin", "pass")
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/dashboard")
