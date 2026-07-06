# app/services/firebase_client.py
import json
import os

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

_firebase_app = None


def init_firebase():
    """Initialize the Firebase Admin SDK once, at app startup.

    Supports either:
    - FIREBASE_CREDENTIALS_JSON env var containing the full service account JSON
      (preferred for Render / hosted envs, no file to manage)
    - FIREBASE_CREDENTIALS_PATH env var pointing to a local firebase-key.json
      (convenient for local dev)
    """
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
    creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")

    if creds_json:
        cred = credentials.Certificate(json.loads(creds_json))
    else:
        cred = credentials.Certificate(creds_path)

    _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def verify_id_token(id_token: str) -> dict:
    """Verifies a Firebase ID token and returns its decoded claims.

    Raises firebase_admin.auth.* exceptions on invalid/expired tokens —
    callers should catch these and turn them into a 401.
    """
    return firebase_auth.verify_id_token(id_token)