# app/services/calendar_matcher.py
from datetime import datetime, timedelta
from app.models.calendar_event import CalendarEvent  # existing model backing /api/calendar

WINDOW_DAYS = 7

def get_upcoming_events():
    today = datetime.utcnow().date()
    events = CalendarEvent.query.filter(CalendarEvent.start_date >= today).order_by(
        CalendarEvent.start_date.asc()
    ).all()
    return events

def find_primary_and_nearby(prompt_text: str):
    """
    Very simple keyword match against upcoming event titles/types
    (PTM, Holiday, Exam, Event) to find the primary event the prompt refers to,
    then finds any other upcoming event within ±7 days of it.
    """
    upcoming = get_upcoming_events()
    prompt_lower = prompt_text.lower()

    primary = None
    for e in upcoming:
        if e.title.lower() in prompt_lower or e.type.lower() in prompt_lower:
            primary = e
            break

    if not primary:
        return None, []

    nearby = []
    for e in upcoming:
        if e.id == primary.id:
            continue
        delta = abs((e.start_date - primary.start_date).days)
        if delta <= WINDOW_DAYS:
            nearby.append(e)

    return primary, nearby