# seed_super.py
from app import create_app
from app.extensions import db
from app.models.admin_user import AdminUser

app = create_app()

with app.app_context():
    email = "ccs.nurturedreams@gmail.com"

    existing = AdminUser.query.filter_by(email=email).first()
    if existing:
        print(f"Already exists: {existing.email} — role: {existing.role}")
    else:
        admin = AdminUser(email=email, role="super_admin")
        db.session.add(admin)
        db.session.commit()
        print(f"Created super_admin: {email}")