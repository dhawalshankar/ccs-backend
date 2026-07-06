# app/services/holidays.py
import holidays as holidays_lib
from app.extensions import db
from app.models.calendar_event import CalendarEvent

# Only these get auto-seeded — everything else on CCS's calendar
# (Ambedkar Jayanti, Raksha Bandhan, Janmashtami, Dussehra, Guru Nanak Jayanti,
# Maha Shivratri, New Year, Shivaji Jayanti, Maharishi Valmiki Jayanti,
# Hazrat Ali's Birthday, Buddha Purnima) has no entry in this library —
# those always need manual entry via the admin panel.
OBSERVED_HOLIDAYS = {
    "Makar Sankranti / Pongal",
    "Republic Day",
    "Holi",
    "Good Friday",
    "Independence Day",
    "Gandhi Jayanti",
    "Diwali",
    "Christmas Day",
    "Eid ul-Fitr",
}

def seed_national_holidays(year: int):
    in_holidays = holidays_lib.country_holidays("IN", years=year)
    added = 0

    for day, name in sorted(in_holidays.items()):
        clean_name = name.split(" (estimated)")[0].split(";")[0].strip()
        if clean_name not in OBSERVED_HOLIDAYS:
            continue

        exists = CalendarEvent.query.filter_by(
            title=clean_name, start_date=day, source="auto"
        ).first()
        if exists:
            continue

        event = CalendarEvent(
            title=clean_name,
            start_date=day,
            end_date=None,
            type="Holiday",
            source="auto",
        )
        db.session.add(event)
        added += 1

    db.session.commit()
    return added