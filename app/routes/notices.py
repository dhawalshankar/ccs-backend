from flask import Blueprint, request, jsonify, Response, current_app
from app.extensions import db
from app.models.notice import Notice
from app.services.docx_convert import convert_docx_to_pdf
from app.services.cloudinary_client import upload_pdf
from app.services.calendar_matcher import find_primary_and_nearby
from app.services.groq_client import generate_notice_draft, extract_fields_from_prompt
from app.services.notice_renderer import render_notice_pdf
import uuid
import requests

notices_bp = Blueprint("notices", __name__, url_prefix="/api/notices")


@notices_bp.get("")
def list_notices():
    notices = Notice.query.filter_by(published=True).order_by(Notice.uploaded_at.desc()).all()
    return jsonify([n.to_dict() for n in notices])


@notices_bp.post("")
def upload_notice():
    title = request.form.get("title")
    file = request.files.get("file")
    if not title or not file:
        return jsonify({"error": "title and file are required"}), 400
    filename = file.filename
    file_bytes = file.read()
    if filename.lower().endswith(".docx"):
        pdf_bytes = convert_docx_to_pdf(file_bytes, filename)
    elif filename.lower().endswith(".pdf"):
        pdf_bytes = file_bytes
    else:
        return jsonify({"error": "Only PDF or DOCX files are supported"}), 400
    public_id = f"notice-{uuid.uuid4().hex[:10]}"
    file_url = upload_pdf(pdf_bytes, public_id)
    notice = Notice(title=title, file_url=file_url, original_filename=filename)
    db.session.add(notice)
    db.session.commit()
    return jsonify(notice.to_dict()), 201


@notices_bp.get("/<int:notice_id>/download")
def download_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    try:
        resp = requests.get(notice.file_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        current_app.logger.error(f"Failed to fetch notice {notice_id} from Cloudinary: {e}")
        return jsonify({"error": "Could not retrieve file"}), 502
    return Response(
        resp.content,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{notice.title}.pdf"'}
    )


@notices_bp.delete("/<int:notice_id>")
def delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    return "", 204


# ---------- Generate Notice (Groq + calendar) ----------

@notices_bp.post("/generate-draft")
def generate_draft():
    data = request.get_json()
    prompt = data.get("prompt", "")

    primary, nearby = find_primary_and_nearby(prompt)
    extracted = extract_fields_from_prompt(prompt)

    if not extracted:
        current_app.logger.warning(
            "Field extraction returned nothing for prompt; falling back to calendar-only fields. prompt=%r",
            prompt,
        )

    def field(name, calendar_fallback=None):
        e = extracted.get(name, {"value": "", "missing": True})
        if not e.get("missing") and e.get("value"):
            return {"value": e["value"], "missing": False}
        if calendar_fallback:
            return {"value": calendar_fallback, "missing": False}
        return {"value": "", "missing": True}

    fields = {
        "school_name": {"value": "Cape Comorin School", "missing": False},
        "principal_name": {"value": "Mrs. Chitranshi Shukla", "missing": False},
        "event_title": field("event_title", primary.title if primary else None),
        "date": field("date", primary.start_date.isoformat() if primary else None),
        "timing": field("timing"),
        "venue": field("venue"),
        "classes": field("classes"),
        "extra_context": field("extra_context"),
    }

    return jsonify({
        "calendar_matched": bool(primary),
        "primary_event": (
            {"title": primary.title, "type": primary.type, "date": primary.start_date.isoformat()}
            if primary else None
        ),
        "fields": fields,
        "raw_prompt": prompt,
        "nearby_events": [
            {"title": e.title, "date": e.start_date.isoformat(), "include": False} for e in nearby
        ],
    })


@notices_bp.post("/generate-draft/confirm")
def confirm_draft():
    data = request.get_json()
    primary_event = data.get("primary_event")  # can be None for one-off notices
    event_title = data.get("event_title")
    date = data.get("date")
    timing = data.get("timing")
    venue = data.get("venue")
    classes = data.get("classes")
    include_events = data.get("include_events", [])
    raw_prompt = data.get("raw_prompt", "")
    extra_context = data.get("extra_context", "")

    draft_text = generate_notice_draft(
        primary_event,
        timing,
        venue,
        classes,
        include_events,
        event_title,
        date,
        raw_prompt=raw_prompt,
        extra_context=extra_context,
    )
    return jsonify({"draft_text": draft_text})


@notices_bp.post("/finalize")
def finalize_notice():
    data = request.get_json()
    final_text = data["final_text"]
    classes = data.get("classes")
    event_title = data.get("event_title", "Notice")

    pdf_bytes = render_notice_pdf(final_text, classes)

    public_id = f"notice-{uuid.uuid4().hex[:10]}"
    file_url = upload_pdf(pdf_bytes, public_id)

    notice = Notice(title=event_title, file_url=file_url, original_filename=f"{event_title}.pdf")
    db.session.add(notice)
    db.session.commit()

    return jsonify(notice.to_dict()), 201