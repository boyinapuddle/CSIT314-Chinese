import sqlite3
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

    def find_by_name(self, name, exclude_profile_id=None):
        if exclude_profile_id is None:
            return self.one(
                "SELECT * FROM user_profiles WHERE lower(name)=lower(?)",
                (name,),
            )
        return self.one(
            "SELECT * FROM user_profiles WHERE lower(name)=lower(?) AND profile_id<>?",
            (name, exclude_profile_id),
        )

    def create(self, name, description, role):
        try:
            return self.execute(
                "INSERT INTO user_profiles(name,description,role) VALUES (?,?,?)",
                (name, description, role),
            ).lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError("A profile with this name already exists.") from error

    def update(self, profile_id, name, description, role):
        return self.execute(
            "UPDATE user_profiles SET name=?,description=?,role=? WHERE profile_id=?",
            (name, description, role, profile_id),
        ).rowcount

    def suspend(self, profile_id):
        return self.execute(
            "UPDATE user_profiles SET status='Suspended' WHERE profile_id=? AND status='Active'",
            (profile_id,),
        ).rowcount

    def reactivate(self, profile_id):
        return self.execute(
            "UPDATE user_profiles SET status='Active' WHERE profile_id=? AND status='Suspended'",
            (profile_id,),
        ).rowcount

    def account_count(self, profile_id):
        row = self.one(
            "SELECT COUNT(*) count FROM user_accounts WHERE profile_id=?",
            (profile_id,),
        )
        return row["count"]

    def delete(self, profile_id):
        return self.execute(
            "DELETE FROM user_profiles WHERE profile_id=?",
            (profile_id,),
        ).rowcount


class AccountRepository(BaseRepository):
    def search(self, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            (
                "SELECT a.*, p.name profile_name, p.role role "
                "FROM user_accounts a "
                "JOIN user_profiles p ON p.profile_id = a.profile_id "
                "WHERE a.username LIKE ? OR a.display_name LIKE ? OR a.email LIKE ? "
                "ORDER BY a.account_id DESC"
            ),
            (value, value, value),
        )

    def get(self, account_id):
        return self.one(
            (
                "SELECT a.*, p.name profile_name, p.role role, p.status profile_status "
                "FROM user_accounts a "
                "JOIN user_profiles p ON p.profile_id = a.profile_id "
                "WHERE a.account_id = ?"
            ),
            (account_id,),
        )

    def by_username(self, username):
        return self.one(
            (
                "SELECT a.*, p.name profile_name, p.role role, p.status profile_status "
                "FROM user_accounts a "
                "JOIN user_profiles p ON p.profile_id = a.profile_id "
                "WHERE a.username = ?"
            ),
            (username,),
        )

    def access_state(self, account_id):
        return self.one(
            (
                "SELECT a.status account_status, p.status profile_status, p.role role "
                "FROM user_accounts a "
                "JOIN user_profiles p ON p.profile_id = a.profile_id "
                "WHERE a.account_id = ?"
            ),
            (account_id,),
        )

    def create(self, username, password_hash, profile_id, display_name, email):
        try:
            return self.execute(
                "INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",
                (username, password_hash, profile_id, display_name, email),
            ).lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError("This username is already in use.") from error

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

    def reactivate(self, account_id):
        return self.execute(
            "UPDATE user_accounts SET status='Active' WHERE account_id=? AND status='Suspended'",
            (account_id,),
        ).rowcount

    def active_admin_count(self, exclude_account_id=None, exclude_profile_id=None):
        sql = "SELECT COUNT(*) count FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.status='Active' AND p.status='Active' AND p.role='User Admin'"
        args = []
        if exclude_account_id is not None:
            sql += " AND a.account_id<>?"
            args.append(exclude_account_id)
        if exclude_profile_id is not None:
            sql += " AND a.profile_id<>?"
            args.append(exclude_profile_id)
        return self.one(sql, tuple(args))["count"]


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

    def find_by_name(self, name):
        return self.one(
            "SELECT * FROM idp_categories WHERE lower(name)=lower(?)",
            (name,),
        )

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

    def reactivate(self, category_id):
        return self.execute(
            "UPDATE idp_categories SET status='Active' WHERE category_id=? AND status='Suspended'",
            (category_id,),
        ).rowcount

    def project_count(self, category_id):
        row = self.one(
            "SELECT COUNT(*) count FROM projects WHERE category_id=?",
            (category_id,),
        )
        return row["count"]

    def delete(self, category_id):
        return self.execute(
            "DELETE FROM idp_categories WHERE category_id=?",
            (category_id,),
        ).rowcount


class ProjectRepository(BaseRepository):
    BASE = (
        "SELECT p.*, c.name category_name, c.status category_status, "
        "a.display_name designer_name, co.name company_name, "
        "CASE WHEN p.visible = 1 AND c.status = 'Active' THEN 1 ELSE 0 END available, "
        "(SELECT COUNT(*) FROM project_views v WHERE v.project_id = p.project_id) views, "
        "(SELECT COUNT(*) FROM favourites f WHERE f.project_id = p.project_id) shortlists "
        "FROM projects p "
        "JOIN idp_categories c ON c.category_id = p.category_id "
        "JOIN user_accounts a ON a.account_id = p.designer_id "
        "LEFT JOIN companies co ON co.designer_id = p.designer_id"
    )

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
            (
                "UPDATE projects "
                "SET category_id = ?, title = ?, description = ?, project_status = ?, "
                "progress = ?, image_url = ?, updated_at = ? "
                "WHERE project_id = ? AND designer_id = ? AND project_status = ?"
            ),
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
    def exists(self, customer_id, project_id):
        return self.one(
            "SELECT favourite_id FROM favourites WHERE customer_id=? AND project_id=?",
            (customer_id, project_id),
        ) is not None

    def add_available(self, customer_id, project_id):
        return self.execute(
            (
                "INSERT OR IGNORE INTO favourites(customer_id, project_id, saved_at) "
                "SELECT ?, p.project_id, ? "
                "FROM projects p "
                "JOIN idp_categories c ON c.category_id = p.category_id "
                "WHERE p.project_id = ? AND p.visible = 1 AND c.status = 'Active'"
            ),
            (customer_id, datetime.utcnow().isoformat(), project_id),
        ).rowcount

    def remove(self, customer_id, project_id):
        return self.execute(
            "DELETE FROM favourites WHERE customer_id=? AND project_id=?",
            (customer_id, project_id),
        ).rowcount

    def search(self, customer_id, keyword=""):
        value = f"%{keyword}%"
        return self.all(
            (
                ProjectRepository.BASE
                + " JOIN favourites fav ON fav.project_id = p.project_id"
                + " WHERE fav.customer_id = ?"
                + " AND (p.title LIKE ? OR p.description LIKE ? OR c.name LIKE ?)"
                + " ORDER BY fav.saved_at DESC"
            ),
            (customer_id, value, value, value),
        )


class ActivityRepository(BaseRepository):
    def log(self, event_type, account_id=None, project_id=None):
        return self.execute(
            "INSERT INTO activity_events(event_type,account_id,project_id,created_at) VALUES(?,?,?,?)",
            (event_type, account_id, project_id, datetime.utcnow().isoformat()),
        ).lastrowid

    def _count_event(self, event_type, start, end):
        row = self.one(
            "SELECT COUNT(*) count FROM activity_events WHERE event_type=? AND created_at BETWEEN ? AND ?",
            (event_type, start, end),
        )
        return row["count"]

    def report(self, start, end):
        active_users = self.one(
            "SELECT COUNT(DISTINCT account_id) count FROM activity_events "
            "WHERE account_id IS NOT NULL AND created_at BETWEEN ? AND ?",
            (start, end),
        )["count"]

        views = self.one(
            "SELECT COUNT(*) count FROM project_views WHERE viewed_at BETWEEN ? AND ?",
            (start, end),
        )["count"]
        unique_viewers = self.one(
            "SELECT COUNT(DISTINCT customer_id) count FROM project_views "
            "WHERE customer_id IS NOT NULL AND viewed_at BETWEEN ? AND ?",
            (start, end),
        )["count"]
        shortlists = self.one(
            "SELECT COUNT(*) count FROM favourites WHERE saved_at BETWEEN ? AND ?",
            (start, end),
        )["count"]

        role_rows = self.all(
            "SELECT p.role, COUNT(DISTINCT ae.account_id) count "
            "FROM activity_events ae "
            "JOIN user_accounts a ON a.account_id=ae.account_id "
            "JOIN user_profiles p ON p.profile_id=a.profile_id "
            "WHERE ae.created_at BETWEEN ? AND ? "
            "GROUP BY p.role",
            (start, end),
        )
        role_activity = {
            "User Admin": 0,
            "Interior Designer": 0,
            "Customer": 0,
            "Platform Manager": 0,
        }
        for row in role_rows:
            role_activity[row["role"]] = row["count"]

        top_viewed_row = self.one(
            "SELECT p.project_id, p.title, COUNT(*) metric "
            "FROM project_views v JOIN projects p ON p.project_id=v.project_id "
            "WHERE v.viewed_at BETWEEN ? AND ? "
            "GROUP BY p.project_id, p.title ORDER BY metric DESC, p.title LIMIT 1",
            (start, end),
        )
        top_shortlisted_row = self.one(
            "SELECT p.project_id, p.title, COUNT(*) metric "
            "FROM favourites f JOIN projects p ON p.project_id=f.project_id "
            "WHERE f.saved_at BETWEEN ? AND ? "
            "GROUP BY p.project_id, p.title ORDER BY metric DESC, p.title LIMIT 1",
            (start, end),
        )

        top_category_row = self.one(
            "WITH view_counts AS ("
            "SELECT p.category_id, COUNT(*) views FROM project_views v "
            "JOIN projects p ON p.project_id=v.project_id "
            "WHERE v.viewed_at BETWEEN ? AND ? GROUP BY p.category_id"
            "), shortlist_counts AS ("
            "SELECT p.category_id, COUNT(*) shortlists FROM favourites f "
            "JOIN projects p ON p.project_id=f.project_id "
            "WHERE f.saved_at BETWEEN ? AND ? GROUP BY p.category_id"
            ") "
            "SELECT c.category_id, c.name, COALESCE(v.views,0) views, "
            "COALESCE(s.shortlists,0) shortlists, "
            "COALESCE(v.views,0)+COALESCE(s.shortlists,0) engagement "
            "FROM idp_categories c "
            "LEFT JOIN view_counts v ON v.category_id=c.category_id "
            "LEFT JOIN shortlist_counts s ON s.category_id=c.category_id "
            "WHERE COALESCE(v.views,0)+COALESCE(s.shortlists,0) > 0 "
            "ORDER BY engagement DESC, c.name LIMIT 1",
            (start, end, start, end),
        )

        top_projects = self.all(
            "WITH views AS ("
            "SELECT project_id, COUNT(*) views FROM project_views "
            "WHERE viewed_at BETWEEN ? AND ? GROUP BY project_id"
            "), shortlists AS ("
            "SELECT project_id, COUNT(*) shortlists FROM favourites "
            "WHERE saved_at BETWEEN ? AND ? GROUP BY project_id"
            ") "
            "SELECT p.project_id, p.title, a.display_name designer_name, "
            "COALESCE(v.views,0) views, COALESCE(s.shortlists,0) shortlists "
            "FROM projects p "
            "JOIN user_accounts a ON a.account_id=p.designer_id "
            "LEFT JOIN views v ON v.project_id=p.project_id "
            "LEFT JOIN shortlists s ON s.project_id=p.project_id "
            "WHERE COALESCE(v.views,0)+COALESCE(s.shortlists,0) > 0 "
            "ORDER BY views DESC, shortlists DESC, p.title LIMIT 5",
            (start, end, start, end),
        )

        category_performance = self.all(
            "WITH views AS ("
            "SELECT p.category_id, COUNT(*) views FROM project_views v "
            "JOIN projects p ON p.project_id=v.project_id "
            "WHERE v.viewed_at BETWEEN ? AND ? GROUP BY p.category_id"
            "), shortlists AS ("
            "SELECT p.category_id, COUNT(*) shortlists FROM favourites f "
            "JOIN projects p ON p.project_id=f.project_id "
            "WHERE f.saved_at BETWEEN ? AND ? GROUP BY p.category_id"
            ") "
            "SELECT c.name, COALESCE(v.views,0) views, COALESCE(s.shortlists,0) shortlists "
            "FROM idp_categories c "
            "LEFT JOIN views v ON v.category_id=c.category_id "
            "LEFT JOIN shortlists s ON s.category_id=c.category_id "
            "WHERE COALESCE(v.views,0)+COALESCE(s.shortlists,0) > 0 "
            "ORDER BY views DESC, shortlists DESC, c.name LIMIT 5",
            (start, end, start, end),
        )

        result = {
            "active_users": active_users,
            "new_accounts": self._count_event("account_created", start, end),
            "successful_logins": self._count_event("login_success", start, end),
            "idps_created": self._count_event("project_created", start, end),
            "idps_updated": self._count_event("project_updated", start, end),
            "views": views,
            "unique_viewers": unique_viewers,
            "shortlists": shortlists,
            "unshortlists": self._count_event("project_unshortlisted", start, end),
            "role_activity": role_activity,
            "top_viewed": dict(top_viewed_row) if top_viewed_row else None,
            "top_shortlisted": dict(top_shortlisted_row) if top_shortlisted_row else None,
            "top_category": dict(top_category_row) if top_category_row else None,
            "top_projects": [dict(row) for row in top_projects],
            "category_performance": [dict(row) for row in category_performance],
        }

        # Backwards-compatible keys used by existing tests and report code.
        result["users"] = result["active_users"]
        result["projects"] = result["idps_updated"]
        return result

