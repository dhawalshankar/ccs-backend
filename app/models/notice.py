# app/models/notice.py
from app.extensions import db
from datetime import datetime

class Notice(db.Model):
    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    original_filename = db.Column(db.String(200))
    published = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "file_url": self.file_url,
            "original_filename": self.original_filename,
            "published": self.published,
            "uploaded_at": self.uploaded_at.isoformat(),
        }