import os
import re
from datetime import datetime
from weasyprint import HTML

SCHOOL_NAME = "Cape Comorin School"
SIGNATURE_NAME = "Chitranshi Shukla"           # cursive signature — no title
PRINCIPAL_NAME = "Mrs. Chitranshi Shukla"      # printed name below — with title

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> app/
LOGO_PATH = "static/logo.png"  # relative to BASE_DIR, resolved via base_url

TEMPLATE = """
<html>
<head>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@700&display=swap');

  body {{ font-family: 'Georgia', serif; margin: 40px; color: #111; }}
  .header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid #111; padding-bottom: 10px; }}
  .header img {{ height: 70px; }}
  .school-name {{ font-family: 'Playfair Display', serif; font-size: 34px; text-align: center; flex: 1; }}
  .date {{ font-size: 14px; text-align: right; white-space: nowrap; }}
  .notice-bar {{ background: #111; color: #fff; text-align: center; font-size: 24px;
                 font-weight: bold; letter-spacing: 4px; padding: 8px 0; margin-top: 10px; }}
  .subtitle {{ text-align: center; font-weight: bold; font-size: 18px; margin: 16px 0; }}
  .body {{ font-size: 16px; line-height: 1.8; margin: 20px 0; }}
  .signature {{ margin-top: 50px; }}
  .signature .sig {{ font-family: 'Dancing Script', cursive; font-size: 42px; color: #2a4d69; }}
  .signature .name {{ font-weight: bold; margin-top: -6px; }}
  .frame {{ border: 2px solid #111; padding: 20px; }}
</style>
</head>
<body>
<div class="frame">
  <div class="header">
    <img src="{logo_path}" />
    <div class="school-name">{school_name}</div>
    <div class="date">Date: {date}</div>
  </div>
  <div class="notice-bar">NOTICE</div>
  <div class="subtitle">(for {classes})</div>
  <div class="body">Dear Parents,<br/><br/>{body}</div>
  <div class="signature">
    Regards,<br/>
    <div class="sig">{signature_name}</div>
    <div class="name">{principal_name}</div>
    Principal
  </div>
</div>
</body>
</html>
"""

def markdown_bold_to_html(text: str) -> str:
    """Convert **bold** markdown into <strong> tags."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

def strip_leading_greeting(text: str) -> str:
    """Remove a leading 'Dear Parents,' line from Groq's output,
    since the template already adds its own greeting."""
    return re.sub(r"^\s*Dear Parents,?\s*\n*", "", text, flags=re.IGNORECASE)

full_logo_path = os.path.join(BASE_DIR, LOGO_PATH)
print(f"DEBUG: Looking for logo at: {full_logo_path}, exists: {os.path.exists(full_logo_path)}")

def render_notice_pdf(body_text: str, classes: str) -> bytes:
    cleaned = strip_leading_greeting(body_text)
    cleaned = markdown_bold_to_html(cleaned)
    cleaned = cleaned.replace("\n", "<br/>")

    html_str = TEMPLATE.format(
        logo_path=LOGO_PATH,
        school_name=SCHOOL_NAME,
        date=datetime.utcnow().strftime("%d %b, %Y"),
        classes=classes or "All Classes",
        body=cleaned,
        signature_name=SIGNATURE_NAME,
        principal_name=PRINCIPAL_NAME,
    )
    return HTML(string=html_str, base_url=BASE_DIR).write_pdf()