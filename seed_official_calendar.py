# seed_official_calendar.py — run once to load the real 2026-27 calendar
from app import create_app
from app.extensions import db
from app.models.calendar_event import CalendarEvent
from datetime import date

app = create_app()

EVENTS = [
    # (title, start, end, type)
    ("New Session Begins", date(2026, 4, 1), None, "Event"),
    ("Good Friday", date(2026, 4, 3), None, "Holiday"),
    ("Ambedkar Jayanti", date(2026, 4, 14), None, "Holiday"),

    ("Buddha Purnima", date(2026, 5, 1), None, "Holiday"),
    ("PTM", date(2026, 5, 16), None, "PTM"),

    ("School Re-Open", date(2026, 7, 1), None, "Event"),
    ("PTM", date(2026, 7, 18), None, "PTM"),

    ("First Term Unit Test", date(2026, 8, 3), date(2026, 8, 11), "Exam"),
    ("Independence Day", date(2026, 8, 15), None, "Holiday"),
    ("1st Term Exam", date(2026, 8, 24), date(2026, 9, 9), "Exam"),
    ("Raksha Bandhan", date(2026, 8, 28), None, "Holiday"),

    ("Janmashtami", date(2026, 9, 4), None, "Holiday"),
    ("Teacher's Day", date(2026, 9, 5), None, "Event"),
    ("PTM (Report Card Distribution)", date(2026, 9, 19), None, "PTM"),

    ("Gandhi Jayanti", date(2026, 10, 2), None, "Holiday"),
    ("Dussehra", date(2026, 10, 20), None, "Holiday"),
    ("Maharishi Valmiki Jayanti", date(2026, 10, 26), None, "Holiday"),

    ("Diwali", date(2026, 11, 7), date(2026, 11, 11), "Holiday"),
    ("2nd Unit Test", date(2026, 11, 12), date(2026, 11, 20), "Exam"),
    ("Children's Day", date(2026, 11, 14), None, "Event"),
    ("Guru Nanak Jayanti", date(2026, 11, 24), None, "Holiday"),

    ("Half Yearly Exam", date(2026, 12, 2), date(2026, 12, 16), "Exam"),
    ("Hazrat Ali's Birthday", date(2026, 12, 23), None, "Holiday"),
    ("Christmas Day", date(2026, 12, 25), None, "Holiday"),
    ("PTM", date(2026, 12, 26), None, "PTM"),

    ("New Year", date(2027, 1, 1), None, "Holiday"),
    ("Makar Sankranti", date(2027, 1, 15), None, "Holiday"),
    ("Republic Day", date(2027, 1, 26), None, "Holiday"),

    ("Monthly Unit Test", date(2027, 2, 1), date(2027, 2, 8), "Exam"),
    ("Shivaji Jayanti", date(2027, 2, 19), None, "Holiday"),

    ("Maha Shivratri", date(2027, 3, 6), None, "Holiday"),
    ("Eid", date(2027, 3, 10), None, "Holiday"),
    ("Annual Examination", date(2027, 3, 1), date(2027, 3, 15), "Exam"),
    ("Holi & Good Friday", date(2027, 3, 22), date(2027, 3, 26), "Holiday"),
    ("PTM (Report Card Distribution)", date(2027, 3, 31), None, "PTM"),
]

with app.app_context():
    added = 0
    for title, start, end, type_ in EVENTS:
        exists = CalendarEvent.query.filter_by(title=title, start_date=start).first()
        if exists:
            continue
        event = CalendarEvent(
            title=title,
            start_date=start,
            end_date=end,
            type=type_,
            source="manual",
        )
        db.session.add(event)
        added += 1
    db.session.commit()
    print(f"Seeded {added} calendar events for session 2026-27.")