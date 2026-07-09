# app/models/admin_user.py
from app.extensions import db
from datetime import datetime

class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)  # must match Firebase auth email
    role = db.Column(db.String(20), nullable=False, default="teacher")  # 'super_admin' | 'teacher'
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=True)  # link to public profile, if any
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "role": self.role, "teacher_id": self.teacher_id}