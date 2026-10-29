from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.database import get_db

app=create_app()
with app.app_context():
    db=get_db()
    for table in ['activity_events','project_views','favourites','projects','companies','user_sessions','user_accounts','idp_categories','user_profiles']:
        db.execute(f'DELETE FROM {table}')
    roles=[('User Admin','Manage user profiles and accounts'),('Interior Designer','Manage company and project portfolio'),('Customer','Explore and save IDPs'),('Platform Manager','Manage categories and reports')]
    db.executemany('INSERT INTO user_profiles(name,description) VALUES(?,?)',roles)
    ids={r['name']:r['profile_id'] for r in db.execute('SELECT * FROM user_profiles')}
    accounts=[
      ('admin',generate_password_hash('Admin123!'),ids['User Admin'],'Avery Admin','admin@example.com'),
      ('designer',generate_password_hash('Designer123!'),ids['Interior Designer'],'Dina Designer','designer@example.com'),
      ('customer',generate_password_hash('Customer123!'),ids['Customer'],'Casey Customer','customer@example.com'),
      ('manager',generate_password_hash('Manager123!'),ids['Platform Manager'],'Morgan Manager','manager@example.com')]
    db.executemany('INSERT INTO user_accounts(username,password_hash,profile_id,display_name,email) VALUES(?,?,?,?,?)',accounts)
    aid={r['username']:r['account_id'] for r in db.execute('SELECT * FROM user_accounts')}
    db.execute('INSERT INTO companies(designer_id,name,description,phone,email,website,address) VALUES(?,?,?,?,?,?,?)',(aid['designer'],'Northline Studio','Residential interiors focused on warm minimalism, practical planning and natural materials.','+65 6123 4567','hello@northline.example','https://example.com','Singapore'))
    cats=[('Modern','Clean lines, restrained palettes and functional layouts'),('Scandinavian','Light woods, calm tones and comfortable simplicity'),('Contemporary','Current materials and refined urban detailing'),('Japandi','Japanese restraint combined with Scandinavian warmth')]
    db.executemany('INSERT INTO idp_categories(name,description) VALUES(?,?)',cats)
    cids={r['name']:r['category_id'] for r in db.execute('SELECT * FROM idp_categories')}
    now=datetime.utcnow()
    projects=[
      (aid['designer'],cids['Modern'],'Tiong Bahru Calm','A compact apartment reworked around hidden storage, soft stone finishes and an open living core.','Current',68,'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=80',(now-timedelta(days=1)).isoformat()),
      (aid['designer'],cids['Japandi'],'Quiet Courtyard Home','A serene family home balancing oak joinery, tactile plaster and carefully framed daylight.','Current',42,'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80',(now-timedelta(days=2)).isoformat()),
      (aid['designer'],cids['Scandinavian'],'Bright Resale Refresh','A completed resale transformation with pale timber, flexible dining and generous concealed storage.','Past',100,'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',(now-timedelta(days=15)).isoformat()),
      (aid['designer'],cids['Contemporary'],'City Lines','A polished apartment with layered lighting, dark accents and a gallery-like living space.','Past',100,'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80',(now-timedelta(days=25)).isoformat())]
    db.executemany('INSERT INTO projects(designer_id,category_id,title,description,project_status,progress,image_url,updated_at) VALUES(?,?,?,?,?,?,?,?)',projects)
    pids=[r['project_id'] for r in db.execute('SELECT project_id FROM projects')]
    for pid in pids:
        for i in range(pid*2):
            db.execute('INSERT INTO project_views(project_id,customer_id,viewed_at) VALUES(?,?,?)',(pid,aid['customer'],(now-timedelta(days=i%5)).isoformat()))
    db.execute('INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)',(aid['customer'],pids[0],now.isoformat()))
    db.execute('INSERT INTO favourites(customer_id,project_id,saved_at) VALUES(?,?,?)',(aid['customer'],pids[2],(now-timedelta(days=2)).isoformat()))
    for et,pid in [('project_viewed',pids[0]),('project_shortlisted',pids[0]),('project_viewed',pids[1]),('project_created',pids[1])]:
        db.execute('INSERT INTO activity_events(event_type,account_id,project_id,created_at) VALUES(?,?,?,?)',(et,aid['customer'],pid,now.isoformat()))
    db.commit()
print('Seeded demo database.')
