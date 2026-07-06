# clear_auto_holidays.py — run once to remove all old unfiltered auto-seed noise
from app import create_app
from app.extensions import db
from app.models.calendar_event import CalendarEvent

app = create_app()

with app.app_context():
    deleted = CalendarEvent.query.filter_by(source="auto").delete()
    db.session.commit()
    print(f"Removed {deleted} auto-seeded entries.")