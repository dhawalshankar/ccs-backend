# app/models/calendar_event.py
from app.extensions import db
from datetime import datetime

class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)   # null = single-day event
    type = db.Column(db.String(50), nullable=False, default="Event")  # Holiday / Exam / Event / PTM
    source = db.Column(db.String(20), nullable=False, default="manual")  # manual / auto
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "type": self.type,
            "source": self.source,
        }