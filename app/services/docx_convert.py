# app/services/docx_convert.py
import requests
import time
from flask import current_app

CLOUDCONVERT_BASE = "https://api.cloudconvert.com/v2"

def convert_docx_to_pdf(file_bytes: bytes, filename: str) -> bytes:
    api_key = current_app.config["CLOUDCONVERT_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}"}

    # 1. Create a job: upload -> convert -> export
    job_resp = requests.post(
        f"{CLOUDCONVERT_BASE}/jobs",
        headers=headers,
        json={
            "tasks": {
                "import-file": {"operation": "import/upload"},
                "convert-file": {
                    "operation": "convert",
                    "input": ["import-file"],
                    "output_format": "pdf",
                },
                "export-file": {
                    "operation": "export/url",
                    "input": ["convert-file"],
                },
            }
        },
    )
    job_resp.raise_for_status()
    job = job_resp.json()["data"]

    import_task = next(t for t in job["tasks"] if t["name"] == "import-file")
    upload_url = import_task["result"]["form"]["url"]
    upload_params = import_task["result"]["form"]["parameters"]

    # 2. Actually upload the file bytes to CloudConvert's signed URL
    upload_resp = requests.post(
        upload_url,
        data=upload_params,
        files={"file": (filename, file_bytes)},
    )
    upload_resp.raise_for_status()

    # 3. Poll job status until finished
    job_id = job["id"]
    for _ in range(30):  # ~30s max wait
        status_resp = requests.get(f"{CLOUDCONVERT_BASE}/jobs/{job_id}", headers=headers)
        status_resp.raise_for_status()
        job_data = status_resp.json()["data"]
        if job_data["status"] == "finished":
            export_task = next(t for t in job_data["tasks"] if t["name"] == "export-file")
            file_url = export_task["result"]["files"][0]["url"]
            pdf_resp = requests.get(file_url)
            pdf_resp.raise_for_status()
            return pdf_resp.content
        if job_data["status"] == "error":
            raise RuntimeError("CloudConvert job failed")
        time.sleep(1)

    raise TimeoutError("CloudConvert conversion took too long")