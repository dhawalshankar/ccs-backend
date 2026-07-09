# app/routes/students.py
from flask import Blueprint, request, jsonify
import requests
from app.services.vritukul_client import search_students, get_student, update_student, list_students
from app.services.require_admin import require_admin

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