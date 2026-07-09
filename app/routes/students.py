# app/routes/students.py
from flask import Blueprint, request, jsonify
import requests
from app.services.vritukul_client import (
    search_students, get_student, update_student, list_students,
    delete_student, delete_students_bulk, dedupe_students,
)
from app.services.require_admin import require_admin, require_role

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


def _call_vritukul(fn, *args, **kwargs):
    """Run a vritukul_client call and turn backend errors into clean JSON
    responses instead of letting requests.HTTPError bubble up unhandled."""
    try:
        return fn(*args, **kwargs), 200
    except requests.exceptions.HTTPError as e:
        detail = e.response.text if e.response is not None else str(e)
        return {"error": "Student service request failed", "detail": detail}, 502
    except requests.exceptions.RequestException as e:
        return {"error": "Could not reach student service", "detail": str(e)}, 502


@students_bp.get("/search")
@require_admin
def search():
    q = request.args.get("q", "")
    body, status = _call_vritukul(search_students, q)
    return jsonify(body), status


@students_bp.get("/sr/<int:sr_number>")
@require_admin
def detail(sr_number):
    body, status = _call_vritukul(get_student, sr_number)
    return jsonify(body), status


@students_bp.patch("/sr/<int:sr_number>")
@require_admin
def edit(sr_number):
    body, status = _call_vritukul(update_student, sr_number, request.get_json())
    return jsonify(body), status


@students_bp.get("/list")
@require_admin
def list_all():
    body, status = _call_vritukul(list_students)
    return jsonify(body), status


# --- Destructive actions: super_admin only ---
# require_admin runs first (authenticates + sets request.user), then
# require_role checks request.user["role"] before the view function runs.

@students_bp.delete("/id/<int:student_id>")
@require_admin
@require_role("super_admin")
def delete_one(student_id):
    body, status = _call_vritukul(delete_student, student_id)
    return jsonify(body), status


@students_bp.post("/delete-bulk")
@require_admin
@require_role("super_admin")
def delete_bulk():
    ids = (request.get_json(silent=True) or {}).get("ids", [])
    if not ids:
        return jsonify({"error": "No ids provided"}), 400
    body, status = _call_vritukul(delete_students_bulk, ids)
    return jsonify(body), status


@students_bp.post("/dedupe")
@require_admin
@require_role("super_admin")
def dedupe():
    dry_run = request.args.get("dry_run", "true").lower() != "false"
    body, status = _call_vritukul(dedupe_students, dry_run)
    return jsonify(body), status