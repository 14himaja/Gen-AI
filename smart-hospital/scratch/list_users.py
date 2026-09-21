from app.database import db
users = db.get_all_users()
for u in users:
    print(u.user_id, u.email, u.name, u.role)
