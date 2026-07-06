# app/routes/__init__.py

from .calendar import calendar_bp
from .fees import fees_bp
from .notices import notices_bp

ROUTES = {
    "Calendar": "/api/calendar",
    "Notices": "/api/notices",
    "Fees": "/api/fees"
}