# app/services/notice_renderer.py
from datetime import datetime
from weasyprint import HTML

SCHOOL_NAME = "Cape Comorin School"
PRINCIPAL_NAME = "Mrs. Chitranshi Shukla"
LOGO_PATH = "app/static/logo.png"

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
    <div class="sig">{principal_name}</div>
    <div class="name">{principal_name}</div>
    Principal
  </div>
</div>
</body>
</html>
"""

def render_notice_pdf(body_text: str, classes: str) -> bytes:
    html_str = TEMPLATE.format(
        logo_path=LOGO_PATH,
        school_name=SCHOOL_NAME,
        date=datetime.utcnow().strftime("%d %b, %Y"),
        classes=classes or "All Classes",
        body=body_text.replace("\n", "<br/>"),
        principal_name=PRINCIPAL_NAME,
    )
    return HTML(string=html_str).write_pdf()