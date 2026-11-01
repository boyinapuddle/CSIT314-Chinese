import os
import tempfile
import pytest
from app import create_app
from app.database import get_db
from werkzeug.security import generate_password_hash


@pytest.fixture()
def app():
    file_descriptor, path = tempfile.mkstemp()
    os.close(file_descriptor)
    app = create_app({"TESTING": True, "DATABASE": path, "SECRET_KEY": "test"})
    with app.app_context():
        db = get_db()
        db.executemany(
            "INSERT INTO user_profiles(name,description,role) VALUES(?,?,?)",
            [
                ("User Admin", "", "User Admin"),
                ("Customer", "", "Customer"),
                ("Interior Designer", "", "Interior Designer"),
                ("Platform Manager", "", "Platform Manager"),
            ],
        )
        profile_id = db.execute(
            "SELECT profile_id FROM user_profiles WHERE name='Customer'"
        ).fetchone()[0]
        db.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            (
                "customer",
                generate_password_hash("pass"),
                profile_id,
                "Test Customer",
                "c@test",
            ),
        )
        db.execute(
            "INSERT INTO idp_categories(name,description) VALUES('Modern','Modern spaces')"
        )
        db.commit()
    yield app
    os.unlink(path)


@pytest.fixture()
def client(app):
    return app.test_client()
