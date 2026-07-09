# app/routes/teachers.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.teacher import Teacher
from app.services.require_admin import require_admin

teachers_bp = Blueprint("teachers", __name__, url_prefix="/api/teachers")

@teachers_bp.get("")
def list_teachers():
    teachers = Teacher.query.order_by(Teacher.display_order.asc()).all()
    return jsonify([t.to_dict() for t in teachers])

@teachers_bp.post("")
@require_admin
def create_teacher():
    data = request.get_json()
    teacher = Teacher(
        name=data["name"],
        subject=data.get("subject"),
        grade_level=data.get("grade_level"),
        bio=data.get("bio"),
        photo_url=data.get("photo_url"),
        display_order=data.get("display_order", 0),
        published=data.get("published", True),
    )
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.to_dict()), 201

@teachers_bp.put("/<int:teacher_id>")
@require_admin
def update_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    data = request.get_json()
    for field in ["name", "subject", "grade_level", "bio", "photo_url", "display_order", "published"]:
        if field in data:
            setattr(teacher, field, data[field])
    db.session.commit()
    return jsonify(teacher.to_dict())

@teachers_bp.delete("/<int:teacher_id>")
@require_admin
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return "", 204