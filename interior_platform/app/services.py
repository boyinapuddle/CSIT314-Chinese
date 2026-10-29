from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from .repositories import *

class PasswordService:
    def hash(self,p): return generate_password_hash(p)
    def verify(self,h,p): return check_password_hash(h,p)

class SessionService:
    def __init__(self): self.repo=SessionRepository()
    def start(self,aid,role): return self.repo.create(aid,role)
    def stop(self,sid): self.repo.invalidate(sid)

class AuthenticationService:
    def __init__(self): self.accounts=AccountRepository(); self.passwords=PasswordService(); self.sessions=SessionService()
    def login(self,u,p,expected_role=None):
        a=self.accounts.by_username(u)
        if not a or a['status']!='Active' or a['profile_status']!='Active': return None
        if expected_role and a['role'] != expected_role: return None
        if not self.passwords.verify(a['password_hash'],p): return None
        return a, self.sessions.start(a['account_id'],a['role'])

class ProfileService:
    def __init__(self): self.repo=ProfileRepository()
    def get(self,pid): return self.repo.get(pid)
    def search(self,q): return self.repo.search(q)
    def create(self,n,d): return self.repo.create(n.strip(),d.strip())
    def update(self,pid,n,d): self.repo.update(pid,n.strip(),d.strip())
    def suspend(self,pid): self.repo.suspend(pid)

class AccountService:
    def __init__(self): self.repo=AccountRepository(); self.passwords=PasswordService()
    def get(self,aid): return self.repo.get(aid)
    def search(self,q): return self.repo.search(q)
    def create(self,u,p,pid,d,e): return self.repo.create(u.strip(),self.passwords.hash(p),pid,d.strip(),e.strip())
    def update(self,aid,d,e,pid): self.repo.update(aid,d.strip(),e.strip(),pid)
    def suspend(self,aid): self.repo.suspend(aid)

class CompanyService:
    def __init__(self): self.repo=CompanyRepository()
    def get(self,did): return self.repo.get_for_designer(did)
    def search(self,did,q): return self.repo.search(did,q)
    def save(self,did,data): self.repo.upsert(did,*[data.get(k,'').strip() for k in ('name','description','phone','email','website','address')])
    def delete(self,did): self.repo.delete(did)

class ProjectService:
    def __init__(self): self.repo=ProjectRepository(); self.activity=ActivityRepository()
    def owned(self,did,status,q): return self.repo.search_owned(did,status,q)
    def available(self,q): return self.repo.search_available(q)
    def create(self,did,data,status):
        pid=self.repo.create(did,int(data['category_id']),data['title'].strip(),data['description'].strip(),status,int(data.get('progress',0)),data.get('image_url','').strip()); self.activity.log('project_created',did,pid); return pid
    def update(self,pid,did,data): self.repo.update_owned(pid,did,int(data['category_id']),data['title'].strip(),data['description'].strip(),data['project_status'],int(data.get('progress',0)),data.get('image_url','').strip())
    def delete(self,pid,did,status): return self.repo.delete_owned(pid,did,status)
    def view(self,pid,cid=None):
        p=self.repo.get(pid)
        if p and p['visible']:
            self.repo.add_view(pid,cid); self.activity.log('project_viewed',cid,pid)
        return p

class FavouriteService:
    def __init__(self): self.repo=FavouriteRepository(); self.projects=ProjectRepository(); self.activity=ActivityRepository()
    def save(self,cid,pid):
        p=self.projects.get(pid)
        if not p or not p['visible']: return False
        added=self.repo.add(cid,pid)
        if added: self.activity.log('project_shortlisted',cid,pid)
        return bool(added)
    def search(self,cid,q): return self.repo.search(cid,q)

class CategoryService:
    def __init__(self): self.repo=CategoryRepository()
    def get(self,cid): return self.repo.get(cid)
    def search(self,q,active_only=False): return self.repo.search(q,active_only)
    def create(self,n,d): return self.repo.create(n.strip(),d.strip())
    def update(self,cid,n,d): self.repo.update(cid,n.strip(),d.strip())
    def suspend(self,cid): self.repo.suspend(cid)

class AnalyticsService:
    def __init__(self): self.projects=ProjectRepository()
    def project_metrics(self,pid):
        p=self.projects.get(pid)
        return {'views': p['views'] if p else 0, 'shortlists': p['shortlists'] if p else 0}
    def designer_metric_rows(self,did,metric):
        rows=list(self.projects.search_owned(did,'Current','')) + list(self.projects.search_owned(did,'Past',''))
        # Keep complete project rows for the UI while making this use case explicit.
        return rows if metric in ('views','shortlists') else []

class ReportService:
    def __init__(self): self.repo=ActivityRepository()
    def generate(self,period,date_value=None):
        now=datetime.utcnow()
        try:
            selected=datetime.fromisoformat(date_value) if date_value else now
        except ValueError:
            selected=now
        if period=='daily':
            start=selected.replace(hour=0,minute=0,second=0,microsecond=0); end=start+timedelta(days=1)-timedelta(microseconds=1)
        elif period=='weekly':
            start=(selected-timedelta(days=selected.weekday())).replace(hour=0,minute=0,second=0,microsecond=0); end=start+timedelta(days=7)-timedelta(microseconds=1)
        else:
            start=selected.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
            end=(start.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(microseconds=1)
        if end>now: end=now
        r=self.repo.report(start.isoformat(),end.isoformat())
        return {'period':period.title(),'from':start.date().isoformat(),'to':end.date().isoformat(),'selected':selected.date().isoformat(),**dict(r)}

class SearchService:
    def global_projects(self,q): return ProjectService().available(q)
