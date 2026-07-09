# app/routes/registers.py
from flask import Blueprint, request, jsonify
from app.services.vritukul_client import upload_register
from app.services.require_admin import require_admin

registers_bp = Blueprint("registers", __name__, url_prefix="/api/registers")

@registers_bp.post("/upload")
@require_admin
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file is required"}), 400
    school_id = request.form.get("school_id", 1, type=int)
    sr_series = request.form.get("sr_series", "old")
    result = upload_register(file.read(), file.filename, school_id, sr_series)
    return jsonify(result)