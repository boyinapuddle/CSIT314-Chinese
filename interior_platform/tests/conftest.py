import os, tempfile, pytest
from app import create_app
from app.database import get_db
from werkzeug.security import generate_password_hash

@pytest.fixture()
def app():
    fd,path=tempfile.mkstemp(); os.close(fd)
    app=create_app({'TESTING':True,'DATABASE':path,'SECRET_KEY':'test'})
    with app.app_context():
        db=get_db();
        db.executemany('INSERT INTO user_profiles(name,description) VALUES(?,?)',[('User Admin',''),('Customer',''),('Interior Designer',''),('Platform Manager','')])
        pid=db.execute("SELECT profile_id FROM user_profiles WHERE name='Customer'").fetchone()[0]
        db.execute('INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)',('customer',generate_password_hash('pass'),pid,'Test Customer','c@test'))
        db.execute("INSERT INTO idp_categories(name,description) VALUES('Modern','Modern spaces')")
        db.commit()
    yield app
    os.unlink(path)

@pytest.fixture()
def client(app): return app.test_client()
