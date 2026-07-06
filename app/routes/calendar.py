# app/routes/calendar.py
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from app.extensions import db
from app.models.calendar_event import CalendarEvent
from app.services.holidays import seed_national_holidays

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")


@calendar_bp.get("")
def list_events():
    today = date.today()

    # Current academic year (April -> March)
    if today.month >= 4:
        start = date(today.year, 4, 1)
        end = date(today.year + 1, 3, 31)
    else:
        start = date(today.year - 1, 4, 1)
        end = date(today.year, 3, 31)

    events = (
        CalendarEvent.query
        .filter(CalendarEvent.start_date >= start)
        .filter(CalendarEvent.start_date <= end)
        .order_by(CalendarEvent.start_date.asc())
        .all()
    )

    return jsonify([e.to_dict() for e in events])

@calendar_bp.post("")
def create_event():
    data = request.get_json()
    event = CalendarEvent(
        title=data["title"],
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None,
        type=data.get("type", "Event"),
        source="manual",
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@calendar_bp.put("/<int:event_id>")
def update_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    data = request.get_json()

    event.title = data.get("title", event.title)

    if data.get("start_date"):
        event.start_date = datetime.strptime(
            data["start_date"], "%Y-%m-%d"
        ).date()

    if data.get("end_date"):
        event.end_date = datetime.strptime(
            data["end_date"], "%Y-%m-%d"
        ).date()

    event.type = data.get("type", event.type)

    db.session.commit()
    return jsonify(event.to_dict())


@calendar_bp.delete("/<int:event_id>")
def delete_event(event_id):
    event = CalendarEvent.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return "", 204


@calendar_bp.post("/seed-holidays")
def seed_holidays():
    year = request.args.get("year", default=date.today().year, type=int)
    added = seed_national_holidays(year)
    return jsonify({"added": added, "year": year})