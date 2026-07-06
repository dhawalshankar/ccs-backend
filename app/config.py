import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")

    USE_TURSO = os.getenv("USE_TURSO", "false").lower() == "true"

    if USE_TURSO:
        turso_url = os.getenv("TURSO_DATABASE_URL")
        turso_token = os.getenv("TURSO_AUTH_TOKEN")

        SQLALCHEMY_DATABASE_URI = (
            f"sqlite+{turso_url}/?authToken={turso_token}&secure=true"
        )

        # Temporary debug
        print("USE_TURSO:", USE_TURSO)
        print("DB URL:", turso_url)
        print("TOKEN PRESENT:", bool(turso_token))
        print("SQLALCHEMY_DATABASE_URI:",
              SQLALCHEMY_DATABASE_URI.replace(turso_token, "***"))

    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///ccs_dev.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")