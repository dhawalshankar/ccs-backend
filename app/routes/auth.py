# app/routes/auth.py
from flask import Blueprint, request, jsonify
from app.services.require_admin import require_admin

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/me")
@require_admin
def me():
    return jsonify({
        "email": request.user.get("email"),
        "role": request.user.get("role"),
        "teacher_id": request.user.get("teacher_id"),
    })