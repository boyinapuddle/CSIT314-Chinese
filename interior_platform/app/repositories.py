from datetime import datetime
from .database import get_db


class BaseRepository:
    @property
    def db(self):
        return get_db()

    def one(self, sql, args=()):
        return self.db.execute(sql, args).fetchone()

    def all(self, sql, args=()):
        return self.db.execute(sql, args).fetchall()

    def execute(self, sql, args=()):
        cursor = self.db.execute(sql, args)
        self.db.commit()
        return cursor


class ProfileRepository(BaseRepository):
    def search(self, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            "SELECT * FROM user_profiles WHERE name LIKE ? OR description LIKE ? ORDER BY name",
            (value, value),
        )

    def get(self, profile_id):
        return self.one("SELECT * FROM user_profiles WHERE profile_id=?", (profile_id,))

    def create(self, name, description):
        return self.execute(
            "INSERT INTO user_profiles(name,description) VALUES (?,?)",
            (name, description),
        ).lastrowid

    def update(self, profile_id, name, description):
        return self.execute(
            "UPDATE user_profiles SET name=?,description=? WHERE profile_id=?",
            (name, description, profile_id),
        ).rowcount

    def suspend(self, profile_id):
        return self.execute(
            "UPDATE user_profiles SET status='Suspended' WHERE profile_id=? AND status='Active'",
            (profile_id,),
        ).rowcount


class AccountRepository(BaseRepository):
    def search(self, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            "SELECT a.*,p.name role FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.username LIKE ? OR a.display_name LIKE ? OR a.email LIKE ? ORDER BY a.account_id DESC",
            (value, value, value),
        )

    def get(self, account_id):
        return self.one(
            "SELECT a.*,p.name role,p.status profile_status FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.account_id=?",
            (account_id,),
        )

    def by_username(self, username):
        return self.one(
            "SELECT a.*,p.name role,p.status profile_status FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.username=?",
            (username,),
        )

    def create(self, username, password_hash, profile_id, display_name, email):
        return self.execute(
            "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
            (username, password_hash, profile_id, display_name, email),
        ).lastrowid

    def update(self, account_id, display_name, email, profile_id):
        return self.execute(
            "UPDATE user_accounts SET display_name=?,email=?,profile_id=? WHERE account_id=?",
            (display_name, email, profile_id, account_id),
        ).rowcount

    def suspend(self, account_id):
        return self.execute(
            "UPDATE user_accounts SET status='Suspended' WHERE account_id=? AND status='Active'",
            (account_id,),
        ).rowcount


class SessionRepository(BaseRepository):
    def create(self, account_id, role):
        return self.execute(
            "INSERT INTO user_sessions(account_id,role,created_at) VALUES(?,?,?)",
            (account_id, role, datetime.utcnow().isoformat()),
        ).lastrowid

    def invalidate(self, session_id):
        return self.execute(
            "UPDATE user_sessions SET active=0 WHERE session_id=?",
            (session_id,),
        ).rowcount

    def active(self, session_id):
        return self.one(
            "SELECT * FROM user_sessions WHERE session_id=? AND active=1",
            (session_id,),
        )


class CompanyRepository(BaseRepository):
    def get_for_designer(self, designer_id):
        return self.one("SELECT * FROM companies WHERE designer_id=?", (designer_id,))

    def search(self, designer_id, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            "SELECT * FROM companies WHERE designer_id=? AND (name LIKE ? OR description LIKE ? OR address LIKE ?)",
            (designer_id, value, value, value),
        )

    def create(self, designer_id, name, description, phone, email, website, address):
        return self.execute(
            "INSERT INTO companies(designer_id,name,description,phone,email,website,address) VALUES(?,?,?,?,?,?,?)",
            (designer_id, name, description, phone, email, website, address),
        ).lastrowid

    def update(self, designer_id, name, description, phone, email, website, address):
        return self.execute(
            "UPDATE companies SET name=?,description=?,phone=?,email=?,website=?,address=? WHERE designer_id=?",
            (name, description, phone, email, website, address, designer_id),
        ).rowcount

    def delete(self, designer_id):
        return self.execute("DELETE FROM companies WHERE designer_id=?", (designer_id,)).rowcount


class CategoryRepository(BaseRepository):
    def search(self, keyword="", active_only=False):
        value = f"%{keyword}%"
        active_clause = " AND status='Active'" if active_only else ""
        return self.all(
            f"SELECT * FROM idp_categories WHERE (name LIKE ? OR description LIKE ?){active_clause} ORDER BY name",
            (value, value),
        )

    def get(self, category_id):
        return self.one("SELECT * FROM idp_categories WHERE category_id=?", (category_id,))

    def create(self, name, description):
        return self.execute(
            "INSERT INTO idp_categories(name,description) VALUES(?,?)",
            (name, description),
        ).lastrowid

    def update(self, category_id, name, description):
        return self.execute(
            "UPDATE idp_categories SET name=?,description=? WHERE category_id=?",
            (name, description, category_id),
        ).rowcount

    def suspend(self, category_id):
        return self.execute(
            "UPDATE idp_categories SET status='Suspended' WHERE category_id=? AND status='Active'",
            (category_id,),
        ).rowcount


class ProjectRepository(BaseRepository):
    BASE = "SELECT p.*,c.name category_name,c.status category_status,a.display_name designer_name,co.name company_name,CASE WHEN p.visible=1 AND c.status='Active' THEN 1 ELSE 0 END available,(SELECT COUNT(*) FROM project_views v WHERE v.project_id=p.project_id) views,(SELECT COUNT(*) FROM favourites f WHERE f.project_id=p.project_id) shortlists FROM projects p JOIN idp_categories c ON c.category_id=p.category_id JOIN user_accounts a ON a.account_id=p.designer_id LEFT JOIN companies co ON co.designer_id=p.designer_id"

    def search_owned(self, designer_id, project_status, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            self.BASE + " WHERE p.designer_id=? AND p.project_status=? AND (p.title LIKE ? OR p.description LIKE ?) ORDER BY p.updated_at DESC",
            (designer_id, project_status, value, value),
        )

    def all_owned(self, designer_id):
        return self.all(
            self.BASE + " WHERE p.designer_id=? ORDER BY p.updated_at DESC",
            (designer_id,),
        )

    def search_available(self, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            self.BASE + " WHERE p.visible=1 AND c.status='Active' AND (p.title LIKE ? OR p.description LIKE ? OR c.name LIKE ?) ORDER BY p.updated_at DESC",
            (value, value, value),
        )

    def get(self, project_id):
        return self.one(self.BASE + " WHERE p.project_id=?", (project_id,))

    def create(self, designer_id, category_id, title, description, project_status, progress, image_url=""):
        return self.execute(
            "INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,?)",
            (
                designer_id,
                category_id,
                title,
                description,
                project_status,
                progress,
                image_url,
                datetime.utcnow().isoformat(),
            ),
        ).lastrowid

    def update_owned(self, project_id, designer_id, category_id, title, description, project_status, progress, image_url):
        return self.execute(
            "UPDATE projects SET category_id=?,title=?,description=?,project_status=?,progress=?,image_url=?,updated_at=? WHERE project_id=? AND designer_id=? AND project_status=?",
            (
                category_id,
                title,
                description,
                project_status,
                progress,
                image_url,
                datetime.utcnow().isoformat(),
                project_id,
                designer_id,
                project_status,
            ),
        ).rowcount

    def delete_owned(self, project_id, designer_id, project_status):
        return self.execute(
            "DELETE FROM projects WHERE project_id=? AND designer_id=? AND project_status=?",
            (project_id, designer_id, project_status),
        ).rowcount

    def add_view(self, project_id, customer_id=None):
        return self.execute(
            "INSERT INTO project_views(project_id,customer_id,viewed_at) VALUES(?,?,?)",
            (project_id, customer_id, datetime.utcnow().isoformat()),
        ).lastrowid


class FavouriteRepository(BaseRepository):
    def add_available(self, customer_id, project_id):
        return self.execute(
            "INSERT OR IGNORE INTO favourites(customer_id,project_id,saved_at) SELECT ?,p.project_id,? FROM projects p JOIN idp_categories c ON c.category_id=p.category_id WHERE p.project_id=? AND p.visible=1 AND c.status='Active'",
            (customer_id, datetime.utcnow().isoformat(), project_id),
        ).rowcount

    def search(self, customer_id, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            ProjectRepository.BASE + " JOIN favourites fav ON fav.project_id=p.project_id WHERE fav.customer_id=? AND (p.title LIKE ? OR p.description LIKE ? OR c.name LIKE ?) ORDER BY fav.saved_at DESC",
            (customer_id, value, value, value),
        )


class ActivityRepository(BaseRepository):
    def log(self, event_type, account_id=None, project_id=None):
        return self.execute(
            "INSERT INTO activity_events(event_type,account_id,project_id,created_at) VALUES(?,?,?,?)",
            (event_type, account_id, project_id, datetime.utcnow().isoformat()),
        ).lastrowid

    def report(self, start, end):
        return self.one(
            "SELECT (SELECT COUNT(*) FROM user_accounts WHERE account_id IN (SELECT account_id FROM activity_events WHERE created_at BETWEEN ? AND ?)) users,(SELECT COUNT(*) FROM projects WHERE updated_at BETWEEN ? AND ?) projects,(SELECT COUNT(*) FROM project_views WHERE viewed_at BETWEEN ? AND ?) views,(SELECT COUNT(*) FROM favourites WHERE saved_at BETWEEN ? AND ?) shortlists",
            (start, end, start, end, start, end, start, end),
        )
