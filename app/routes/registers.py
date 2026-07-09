# app/routes/registers.py
from flask import Blueprint, request, jsonify
from app.services.vritukul_client import upload_register
from app.services.require_admin import require_admin
import requests

registers_bp = Blueprint("registers", __name__, url_prefix="/api/registers")

@registers_bp.post("/upload")
@require_admin
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file is required"}), 400
    school_id = request.form.get("school_id", 1, type=int)
    sr_series = request.form.get("sr_series", "old")
    try:
        result = upload_register(file.read(), file.filename, school_id, sr_series)
        return jsonify(result)
    except requests.exceptions.HTTPError as e:
        return jsonify({
            "error": "Register processing failed",
            "detail": e.response.text if e.response is not None else str(e)
        }), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Could not reach register service", "detail": str(e)}), 502