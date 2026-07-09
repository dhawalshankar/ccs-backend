# app/services/firebase_client.py
import json
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

_firebase_app = None
_init_error = None

def init_firebase():
    global _firebase_app, _init_error
    if _firebase_app is not None:
        return _firebase_app
    if _init_error is not None:
        raise _init_error

    try:
        creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")

        if creds_json:
            cred = credentials.Certificate(json.loads(creds_json))
        elif os.getenv("FIREBASE_PROJECT_ID"):
            service_account_info = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL', '').replace('@', '%40')}",
            }
            cred = credentials.Certificate(service_account_info)
        else:
            cred = credentials.Certificate(creds_path)

        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app

    except Exception as e:
        _init_error = RuntimeError(f"Firebase init failed: {e}")
        print(f"[WARNING] {_init_error} — admin auth routes will return 500 until this is fixed.")
        return None

def verify_id_token(id_token: str) -> dict:
    if _firebase_app is None:
        raise RuntimeError("Firebase is not initialized — check FIREBASE_* env vars")
    return firebase_auth.verify_id_token(id_token)