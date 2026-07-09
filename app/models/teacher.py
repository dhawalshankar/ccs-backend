# app/models/teacher.py
from app.extensions import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(100), nullable=True)
    grade_level = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "bio": self.bio,
            "photo_url": self.photo_url,
            "display_order": self.display_order,
            "published": self.published,
        }