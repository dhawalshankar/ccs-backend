# app/services/require_admin.py
from functools import wraps
from flask import request, jsonify
from app.services.firebase_client import verify_id_token
from app.models.admin_user import AdminUser
import firebase_admin.auth as fb_auth

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        id_token = auth_header.split("Bearer ")[1]
        try:
            decoded = verify_id_token(id_token)
        except fb_auth.ExpiredIdTokenError:
            return jsonify({"error": "Token expired"}), 401
        except fb_auth.InvalidIdTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": "Auth failed", "detail": str(e)}), 401

        admin_user = AdminUser.query.filter_by(email=decoded.get("email")).first()
        if admin_user is None:
            return jsonify({"error": "User not recognized as staff"}), 403

        decoded["role"] = admin_user.role
        decoded["teacher_id"] = admin_user.teacher_id
        request.user = decoded

        return f(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.user.get("role") not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator