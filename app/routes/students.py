# app/routes/students.py
from flask import Blueprint, request, jsonify
from app.services.vritukul_client import search_students, get_student, update_student
from app.services.require_admin import require_admin
# app/routes/students.py — add this route
from app.services.vritukul_client import list_students

students_bp = Blueprint("students", __name__, url_prefix="/api/students")

@students_bp.get("/search")
@require_admin
def search():
    q = request.args.get("q", "")
    return jsonify(search_students(q))

@students_bp.get("/sr/<int:sr_number>")
@require_admin
def detail(sr_number):
    return jsonify(get_student(sr_number))

@students_bp.patch("/sr/<int:sr_number>")
@require_admin
def edit(sr_number):
    return jsonify(update_student(sr_number, request.get_json()))

@students_bp.get("/list")
@require_admin
def list_all():
    return jsonify(list_students())