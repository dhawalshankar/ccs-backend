# app/services/vritukul_client.py
import requests
from flask import current_app

def _headers():
    return {"X-Service-Key": current_app.config["VRITUKUL_SERVICE_KEY"]}

def list_students():
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.get(f"{base}/api/students/list", headers=_headers(), timeout=60)
    res.raise_for_status()
    return res.json()

def search_students(query: str):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.get(f"{base}/api/students/search", params={"q": query}, headers=_headers(), timeout=30)
    res.raise_for_status()
    return res.json()

def get_student(sr_number: int):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.get(f"{base}/api/students/sr/{sr_number}", headers=_headers(), timeout=30)
    res.raise_for_status()
    return res.json()

def update_student(sr_number: int, data: dict):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.patch(f"{base}/api/students/sr/{sr_number}", json=data, headers=_headers(), timeout=30)
    res.raise_for_status()
    return res.json()

def create_student(data: dict):
    """data must include student_name and sr_series ('old' or 'new'),
    plus any of the other optional student fields."""
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.post(f"{base}/api/students/create", json=data, headers=_headers(), timeout=30)
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
        timeout=180,
    )
    res.raise_for_status()
    return res.json()

def delete_student(student_id: int):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.delete(f"{base}/api/students/id/{student_id}", headers=_headers(), timeout=30)
    res.raise_for_status()
    return res.json()

def delete_students_bulk(ids: list):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.post(
        f"{base}/api/students/delete-bulk",
        json={"ids": ids},
        headers=_headers(),
        timeout=60,
    )
    res.raise_for_status()
    return res.json()

def dedupe_students(dry_run: bool = True):
    base = current_app.config["VRITUKUL_BASE_URL"]
    res = requests.post(
        f"{base}/api/students/dedupe",
        params={"dry_run": str(dry_run).lower()},
        headers=_headers(),
        timeout=120,
    )
    res.raise_for_status()
    return res.json()