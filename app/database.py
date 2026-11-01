import sqlite3
from pathlib import Path
from flask import current_app, g

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS user_profiles (
 profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT UNIQUE NOT NULL, description TEXT NOT NULL DEFAULT '',
 role TEXT NOT NULL DEFAULT 'Customer' CHECK(role IN ('User Admin','Interior Designer','Customer','Platform Manager')),
 status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Suspended'))
);
CREATE TABLE IF NOT EXISTS user_accounts (
 account_id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
 profile_id INTEGER NOT NULL, display_name TEXT NOT NULL, email TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active','Suspended')),
 FOREIGN KEY(profile_id) REFERENCES user_profiles(profile_id)
);
CREATE TABLE IF NOT EXISTS user_sessions (
 session_id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER NOT NULL,
 role TEXT NOT NULL, created_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
 FOREIGN KEY(account_id) REFERENCES user_accounts(account_id)
);
CREATE TABLE IF NOT EXISTS companies (
 company_id INTEGER PRIMARY KEY AUTOINCREMENT, designer_id INTEGER UNIQUE NOT NULL,
 name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT '',
 email TEXT NOT NULL DEFAULT '', website TEXT NOT NULL DEFAULT '', address TEXT NOT NULL DEFAULT '',
 FOREIGN KEY(designer_id) REFERENCES user_accounts(account_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS idp_categories (
 category_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL,
 description TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Active'
);
CREATE TABLE IF NOT EXISTS projects (
 project_id INTEGER PRIMARY KEY AUTOINCREMENT, designer_id INTEGER NOT NULL,
 category_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL,
 project_status TEXT NOT NULL CHECK(project_status IN ('Current','Past')),
 progress INTEGER NOT NULL DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
 image_url TEXT NOT NULL DEFAULT '', visible INTEGER NOT NULL DEFAULT 1,
 updated_at TEXT NOT NULL,
 FOREIGN KEY(designer_id) REFERENCES user_accounts(account_id) ON DELETE CASCADE,
 FOREIGN KEY(category_id) REFERENCES idp_categories(category_id)
);
CREATE TABLE IF NOT EXISTS favourites (
 favourite_id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL,
 project_id INTEGER NOT NULL, saved_at TEXT NOT NULL,
 UNIQUE(customer_id, project_id),
 FOREIGN KEY(customer_id) REFERENCES user_accounts(account_id) ON DELETE CASCADE,
 FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS project_views (
 view_id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL,
 customer_id INTEGER, viewed_at TEXT NOT NULL,
 FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS activity_events (
 event_id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL,
 account_id INTEGER, project_id INTEGER, created_at TEXT NOT NULL
);
"""

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    columns = {row["name"] for row in db.execute("PRAGMA table_info(user_profiles)")}
    if "role" not in columns:
        db.execute("ALTER TABLE user_profiles ADD COLUMN role TEXT NOT NULL DEFAULT 'Customer'")
        db.execute("UPDATE user_profiles SET role=name WHERE name IN ('User Admin','Interior Designer','Customer','Platform Manager')")
    db.commit()

def init_app(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
