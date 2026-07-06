# app/services/cloudinary_client.py
import cloudinary
import cloudinary.uploader
from flask import current_app

def init_cloudinary():
    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
    )

def upload_pdf(file_bytes: bytes, public_id: str) -> str:
    init_cloudinary()
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",       # PDFs go as raw, not "image"
        public_id=public_id,
        folder="ccs-notices",
        format="pdf",
    )
    return result["secure_url"]