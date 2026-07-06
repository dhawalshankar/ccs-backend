# app/routes/notices.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.notice import Notice
from app.services.docx_convert import convert_docx_to_pdf
from app.services.cloudinary_client import upload_pdf
import uuid

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

@notices_bp.delete("/<int:notice_id>")
def delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    return "", 204