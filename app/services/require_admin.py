# app/services/require_admin.py
from functools import wraps
from flask import request, jsonify
from app.services.firebase_client import verify_id_token
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
            request.user = decoded
        except fb_auth.ExpiredIdTokenError:
            return jsonify({"error": "Token expired"}), 401
        except fb_auth.InvalidIdTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": "Auth failed", "detail": str(e)}), 401

        return f(*args, **kwargs)
    return wrapper