from datetime import datetime
from .database import get_db

class BaseRepository:
    @property
    def db(self): return get_db()
    def one(self, sql, args=()): return self.db.execute(sql, args).fetchone()
    def all(self, sql, args=()): return self.db.execute(sql, args).fetchall()
    def execute(self, sql, args=()):
        cur = self.db.execute(sql, args); self.db.commit(); return cur

class ProfileRepository(BaseRepository):
    def search(self, q=""):
        return self.all("SELECT * FROM user_profiles WHERE name LIKE ? OR description LIKE ? ORDER BY name", (f"%{q}%", f"%{q}%"))
    def get(self, pid): return self.one("SELECT * FROM user_profiles WHERE profile_id=?", (pid,))
    def create(self, name, description): return self.execute("INSERT INTO user_profiles(name,description) VALUES (?,?)", (name,description)).lastrowid
    def update(self,pid,name,description): self.execute("UPDATE user_profiles SET name=?,description=? WHERE profile_id=?",(name,description,pid))
    def suspend(self,pid): self.execute("UPDATE user_profiles SET status='Suspended' WHERE profile_id=?",(pid,))

class AccountRepository(BaseRepository):
    def search(self,q=""):
        return self.all("""SELECT a.*,p.name role FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id
        WHERE a.username LIKE ? OR a.display_name LIKE ? OR a.email LIKE ? ORDER BY a.account_id DESC""",(f"%{q}%",)*3)
    def get(self,aid): return self.one("SELECT a.*,p.name role,p.status profile_status FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.account_id=?",(aid,))
    def by_username(self,u): return self.one("SELECT a.*,p.name role,p.status profile_status FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE a.username=?",(u,))
    def create(self,u,h,pid,d,e): return self.execute("INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)",(u,h,pid,d,e)).lastrowid
    def update(self,aid,d,e,pid): self.execute("UPDATE user_accounts SET display_name=?,email=?,profile_id=? WHERE account_id=?",(d,e,pid,aid))
    def suspend(self,aid): self.execute("UPDATE user_accounts SET status='Suspended' WHERE account_id=?",(aid,))

class SessionRepository(BaseRepository):
    def create(self,account_id,role): return self.execute("INSERT INTO user_sessions(account_id,role,created_at) VALUES(?,?,?)",(account_id,role,datetime.utcnow().isoformat())).lastrowid
    def invalidate(self,sid): self.execute("UPDATE user_sessions SET active=0 WHERE session_id=?",(sid,))
    def active(self,sid): return self.one("SELECT * FROM user_sessions WHERE session_id=? AND active=1",(sid,))

class CompanyRepository(BaseRepository):
    def get_for_designer(self,did): return self.one("SELECT * FROM companies WHERE designer_id=?",(did,))
    def search(self,did,q=""): return self.all("SELECT * FROM companies WHERE designer_id=? AND (name LIKE ? OR description LIKE ? OR address LIKE ?)",(did,f"%{q}%",f"%{q}%",f"%{q}%"))
    def upsert(self,did,name,description,phone,email,website,address):
        self.execute("""INSERT INTO companies(designer_id,name,description,phone,email,website,address) VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(designer_id) DO UPDATE SET name=excluded.name,description=excluded.description,phone=excluded.phone,email=excluded.email,website=excluded.website,address=excluded.address""",(did,name,description,phone,email,website,address))
    def delete(self,did): self.execute("DELETE FROM companies WHERE designer_id=?",(did,))

class CategoryRepository(BaseRepository):
    def search(self,q="",active_only=False):
        extra=" AND status='Active'" if active_only else ""
        return self.all(f"SELECT * FROM idp_categories WHERE (name LIKE ? OR description LIKE ?){extra} ORDER BY name",(f"%{q}%",f"%{q}%"))
    def get(self,cid): return self.one("SELECT * FROM idp_categories WHERE category_id=?",(cid,))
    def create(self,n,d): return self.execute("INSERT INTO idp_categories(name,description) VALUES(?,?)",(n,d)).lastrowid
    def update(self,cid,n,d): self.execute("UPDATE idp_categories SET name=?,description=? WHERE category_id=?",(n,d,cid))
    def suspend(self,cid): self.execute("UPDATE idp_categories SET status='Suspended' WHERE category_id=?",(cid,))

class ProjectRepository(BaseRepository):
    BASE="""SELECT p.*,c.name category_name,a.display_name designer_name,co.name company_name,
    (SELECT COUNT(*) FROM project_views v WHERE v.project_id=p.project_id) views,
    (SELECT COUNT(*) FROM favourites f WHERE f.project_id=p.project_id) shortlists
    FROM projects p JOIN idp_categories c ON c.category_id=p.category_id
    JOIN user_accounts a ON a.account_id=p.designer_id LEFT JOIN companies co ON co.designer_id=p.designer_id"""
    def search_owned(self,did,status,q=""):
        return self.all(self.BASE+" WHERE p.designer_id=? AND p.project_status=? AND (p.title LIKE ? OR p.description LIKE ?) ORDER BY p.updated_at DESC",(did,status,f"%{q}%",f"%{q}%"))
    def search_available(self,q=""):
        return self.all(self.BASE+" WHERE p.visible=1 AND c.status='Active' AND (p.title LIKE ? OR p.description LIKE ? OR c.name LIKE ?) ORDER BY p.updated_at DESC",(f"%{q}%",)*3)
    def get(self,pid): return self.one(self.BASE+" WHERE p.project_id=?",(pid,))
    def create(self,did,cid,t,d,s,prog,img=""):
        return self.execute("INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,?)",(did,cid,t,d,s,prog,img,datetime.utcnow().isoformat())).lastrowid
    def update_owned(self,pid,did,cid,t,d,status,prog,img):
        self.execute("UPDATE projects SET category_id=?,title=?,description=?,project_status=?,progress=?,image_url=?,updated_at=? WHERE project_id=? AND designer_id=?",(cid,t,d,status,prog,img,datetime.utcnow().isoformat(),pid,did))
    def delete_owned(self,pid,did,status): return self.execute("DELETE FROM projects WHERE project_id=? AND designer_id=? AND project_status=?",(pid,did,status)).rowcount
    def add_view(self,pid,cid=None): self.execute("INSERT INTO project_views(project_id,customer_id,viewed_at) VALUES(?,?,?)",(pid,cid,datetime.utcnow().isoformat()))

class FavouriteRepository(BaseRepository):
    def add(self,cid,pid): return self.execute("INSERT OR IGNORE INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)",(cid,pid,datetime.utcnow().isoformat())).rowcount
    def search(self,cid,q=""):
        return self.all(ProjectRepository.BASE+" JOIN favourites fav ON fav.project_id=p.project_id WHERE fav.customer_id=? AND (p.title LIKE ? OR p.description LIKE ? OR c.name LIKE ?) ORDER BY fav.saved_at DESC",(cid,f"%{q}%",f"%{q}%",f"%{q}%"))

class ActivityRepository(BaseRepository):
    def log(self,t,aid=None,pid=None): self.execute("INSERT INTO activity_events(event_type,account_id,project_id,created_at) VALUES(?,?,?,?)",(t,aid,pid,datetime.utcnow().isoformat()))
    def report(self,start,end):
        return self.one("""SELECT
        (SELECT COUNT(*) FROM user_accounts WHERE account_id IN (SELECT account_id FROM activity_events WHERE created_at BETWEEN ? AND ?)) users,
        (SELECT COUNT(*) FROM projects WHERE updated_at BETWEEN ? AND ?) projects,
        (SELECT COUNT(*) FROM project_views WHERE viewed_at BETWEEN ? AND ?) views,
        (SELECT COUNT(*) FROM favourites WHERE saved_at BETWEEN ? AND ?) shortlists""",(start,end,start,end,start,end,start,end))
