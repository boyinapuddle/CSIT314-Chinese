"""Deterministic large-volume test data generator for later system/testing evidence."""
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.database import get_db

SEED=2026
random.seed(SEED)
app=create_app()
with app.app_context():
    db=get_db()
    profiles={r['name']:r['profile_id'] for r in db.execute('SELECT * FROM user_profiles')}
    cats=[r['category_id'] for r in db.execute("SELECT category_id FROM idp_categories WHERE status='Active'")]
    if not profiles or not cats:
        raise SystemExit('Run python seed.py first.')
    # 100 designers + companies, 500 customers, 2,000 projects, ~25k views and ~4k favourites.
    for i in range(100):
        u=f'designer{i:03d}'
        cur=db.execute('INSERT OR IGNORE INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)',(u,generate_password_hash('Test123!'),profiles['Interior Designer'],f'Designer {i}',f'{u}@test.local'))
        row=db.execute('SELECT account_id FROM user_accounts WHERE username=?',(u,)).fetchone(); did=row[0]
        db.execute('INSERT OR IGNORE INTO companies(designer_id,name,description) VALUES(?,?,?)',(did,f'Studio {i:03d}','Generated scale-test company'))
    for i in range(500):
        u=f'customer{i:04d}'
        db.execute('INSERT OR IGNORE INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)',(u,generate_password_hash('Test123!'),profiles['Customer'],f'Customer {i}',f'{u}@test.local'))
    designers=[r[0] for r in db.execute("SELECT a.account_id FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE p.name='Interior Designer'")]
    customers=[r[0] for r in db.execute("SELECT a.account_id FROM user_accounts a JOIN user_profiles p ON p.profile_id=a.profile_id WHERE p.name='Customer'")]
    existing=db.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
    for i in range(existing,2000):
        status='Past' if i%3==0 else 'Current'; prog=100 if status=='Past' else random.randint(5,95)
        db.execute('INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,updated_at) VALUES(?,?,?,?,?,?,?)',(random.choice(designers),random.choice(cats),f'Scale Project {i:04d}',f'Generated project description {i}',status,prog,(datetime.utcnow()-timedelta(days=random.randint(0,180))).isoformat()))
    projects=[r[0] for r in db.execute('SELECT project_id FROM projects')]
    for _ in range(25000):
        db.execute('INSERT INTO project_views(project_id,customer_id,viewed_at) VALUES(?,?,?)',(random.choice(projects),random.choice(customers),(datetime.utcnow()-timedelta(days=random.randint(0,90))).isoformat()))
    for _ in range(5000):
        db.execute('INSERT OR IGNORE INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)',(random.choice(customers),random.choice(projects),(datetime.utcnow()-timedelta(days=random.randint(0,90))).isoformat()))
    db.commit()
    print('Large deterministic test dataset generated.')
