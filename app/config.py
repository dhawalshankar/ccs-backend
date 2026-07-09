import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///ccs_dev.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    VRITUKUL_BASE_URL = os.getenv("VRITUKUL_BASE_URL")
    VRITUKUL_SERVICE_KEY = os.getenv("VRITUKUL_SERVICE_KEY")