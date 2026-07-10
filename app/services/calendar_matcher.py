# app/services/calendar_matcher.py
import re
from datetime import datetime
from app.models.calendar_event import CalendarEvent

WINDOW_DAYS = 7
STOPWORDS = {"day", "the", "a", "an", "of", "on", "for", "and", "in", "at", "is", "hai", "ko"}


def get_upcoming_events():
    today = datetime.utcnow().date()
    events = CalendarEvent.query.filter(CalendarEvent.start_date >= today).order_by(
        CalendarEvent.start_date.asc()
    ).all()
    return events


def _significant_words(text: str):
    """Extract meaningful words from a title, excluding common stopwords."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def find_primary_and_nearby(prompt_text: str):
    """
    Matches based on meaningful overlap between the event TITLE's significant
    words and the prompt — never matches on the generic `type` field alone,
    since words like "Holiday"/"Event"/"Exam" are too common to be reliable.
    """
    upcoming = get_upcoming_events()
    prompt_lower = prompt_text.lower()

    best_match = None
    best_score = 0

    for e in upcoming:
        title_words = _significant_words(e.title)
        if not title_words:
            continue
        overlap = sum(1 for w in title_words if w in prompt_lower)
        score = overlap / len(title_words)  # fraction of title's meaningful words found in prompt

        # Require a strong majority of the title's own words to appear in the prompt —
        # this prevents a single generic shared word from causing a false match.
        if score >= 0.6 and overlap > 0 and score > best_score:
            best_score = score
            best_match = e

    if not best_match:
        return None, []

    nearby = []
    for e in upcoming:
        if e.id == best_match.id:
            continue
        delta = abs((e.start_date - best_match.start_date).days)
        if delta <= WINDOW_DAYS:
            nearby.append(e)

    return best_match, nearby