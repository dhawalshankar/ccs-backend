# app/services/vritukul_client.py
import requests
from flask import current_app

def _headers():
    return {"X-Service-Key": current_app.config["VRITUKUL_SERVICE_KEY"]}

def search_students(query: str):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.get(f"{base}/api/students/search", params={"q": query}, headers=_headers())
    res.raise_for_status()
    return res.json()

def get_student(sr_number: int):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.get(f"{base}/api/students/sr/{sr_number}", headers=_headers())
    res.raise_for_status()
    return res.json()

def update_student(sr_number: int, data: dict):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.patch(f"{base}/api/students/sr/{sr_number}", json=data, headers=_headers())
    res.raise_for_status()
    return res.json()

def upload_register(file_bytes: bytes, filename: str, school_id: int = 1, sr_series: str = "old"):
    base = current_app.config["VRITUKUL_BASE_URL"]
    files = {"file": (filename, file_bytes, "application/pdf")}
    params = {"school_id": school_id, "sr_series": sr_series}
    res = requests.post(
        f"{base}/api/registers/upload",
        files=files,
        params=params,
        headers=_headers(),
    )
    res.raise_for_status()
    return res.json()