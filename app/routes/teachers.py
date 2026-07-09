# app/routes/teachers.py
import secrets
import firebase_admin.auth as fb_auth
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.teacher import Teacher
from app.models.admin_user import AdminUser
from app.services.teacher_email import generate_teacher_email
from app.services.require_admin import require_admin, require_role

teachers_bp = Blueprint("teachers", __name__, url_prefix="/api/teachers")


@teachers_bp.get("/")
@require_admin
@require_role("super_admin")
def list_teachers():
    """Internal staff roster — not public. Returns everyone, including inactive."""
    teachers = Teacher.query.order_by(Teacher.display_order).all()
    return jsonify([t.to_dict() for t in teachers])


@teachers_bp.post("/")
@require_admin
@require_role("super_admin")
def create_teacher():
    data = request.get_json()

    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    teacher = Teacher(
        name=data["name"],
        subject=data.get("subject"),
        grade_level=data.get("grade_level"),
        bio=data.get("bio"),
        photo_url=data.get("photo_url"),
    )
    db.session.add(teacher)
    db.session.flush()

    login_email = generate_teacher_email(data["name"])
    temp_password = secrets.token_urlsafe(12)
    try:
        fb_auth.create_user(email=login_email, password=temp_password)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Firebase user creation failed: {e}"}), 500

    admin_user = AdminUser(email=login_email, role="teacher", teacher_id=teacher.id)
    db.session.add(admin_user)
    db.session.commit()

    return jsonify({
        "teacher": teacher.to_dict(),
        "login_email": login_email,
        "temp_password": temp_password,
    })


@teachers_bp.put("/<int:teacher_id>")
@require_admin
@require_role("super_admin")
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
@require_role("super_admin")
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    admin_user = AdminUser.query.filter_by(teacher_id=teacher.id).first()
    if admin_user:
        try:
            fb_auth.delete_user(fb_auth.get_user_by_email(admin_user.email).uid)
        except fb_auth.UserNotFoundError:
            pass  # already gone from Firebase, fine to continue
        except Exception as e:
            return jsonify({"error": f"Couldn't remove Firebase login: {e}"}), 500
        db.session.delete(admin_user)

    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"status": "deleted", "id": teacher_id})