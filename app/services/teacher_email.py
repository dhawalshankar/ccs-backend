# app/services/teacher_email.py
import re
from app.models.teacher import Teacher

def slugify_name(name: str) -> list[str]:
    name = name.lower()
    name = re.sub(r"^(mr|mrs|ms|miss|dr)\.?\s+", "", name)  # strip honorifics
    name = re.sub(r"[^a-z\s]", "", name)  # strip anything not a letter/space
    return name.split()

def generate_teacher_email(full_name: str, domain: str = "capecomorinschool.com") -> str:
    parts = slugify_name(full_name)
    if not parts:
        raise ValueError("Cannot generate email from empty name")

    first = parts[0]
    candidate = f"{first}@{domain}"

    # NOTE: this checks the Teacher table's associated login,
    # but login emails actually live on AdminUser — see note below
    from app.models.admin_user import AdminUser

    if not AdminUser.query.filter_by(email=candidate).first():
        return candidate

    if len(parts) > 1:
        candidate = f"{first}{parts[-1][0]}@{domain}"
        if not AdminUser.query.filter_by(email=candidate).first():
            return candidate

    n = 2
    while True:
        suffix = parts[-1][0] if len(parts) > 1 else ""
        candidate = f"{first}{suffix}{n}@{domain}"
        if not AdminUser.query.filter_by(email=candidate).first():
            return candidate
        n += 1