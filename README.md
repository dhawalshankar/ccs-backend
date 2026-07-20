# CCS Backend (ccs-backend)

**Private, proprietary repository.** This is the backend for the internal **Cape Comorin School (CCS)** ERP/website system — powering [capecomorinschool.com](https://capecomorinschool.com) and its admin panel at `admin.capecomorinschool.com`. Not open source; not for external distribution. Access restricted to the CCS engineering/ops team.

---

## What this service is

This is the **only backend the frontend talks to.** It owns all CCS-specific logic (fees, notices, calendar, teachers, registers) and internally proxies to **Vritukul** — a separate, already-deployed service — for anything records-related: students and register/attendance uploads.

```
Frontend (public site + admin.capecomorinschool.com)
        ↓ (only talks to)
Flask backend (this repo)
        ↓ (proxies to, when needed)
Vritukul (external service, deployed separately)
```

**Key principle:** Vritukul stays completely untouched by this repo. Its footprint here is two env vars (`VRITUKUL_BASE_URL`, `VRITUKUL_SERVICE_KEY`) and a single client file, `app/services/vritukul_client.py`. Nothing else in this codebase needs to know it exists — `routes/students.py` and `routes/registers.py` just call into that client and translate its responses/errors into this API's JSON shape.

---

## Tech Stack

| Area | Choice |
|---|---|
| Framework | Flask |
| Database | **Neon** (serverless Postgres) via Flask-SQLAlchemy — SQLite fallback for local dev |
| Records backend | Vritukul (external, accessed only via proxy — students + registers) |
| Auth (admin panel) | Firebase Admin SDK (JWT/ID token verification) |
| File storage | Cloudinary (CCS's own account, for notice PDFs) |
| Notice storage | PDF/DOCX uploads; DOCX auto-converted to PDF via CloudConvert |
| AI notice drafting | Groq (matches a prompt to calendar events, drafts notice text) |
| Fee payment | Razorpay |
| Academic calendar | National holidays auto-seeded; school-specific entries added manually |
| CORS | Flask-CORS |
| Deployment | Render |

---

## Project Structure

```
ccs-backend/
├── app/
│   ├── __init__.py               # app factory
│   ├── config.py
│   ├── extensions.py             # db, cors
│   ├── routes/
│   │   ├── auth.py               # /api/auth — admin session info
│   │   ├── teachers.py           # /api/teachers — full CRUD, owned entirely by this backend
│   │   ├── students.py           # /api/students — proxied to Vritukul
│   │   ├── registers.py          # /api/registers — proxied to Vritukul's extraction pipeline
│   │   ├── notices.py            # /api/notices — upload, AI-draft, publish, delete
│   │   ├── calendar.py           # /api/calendar — CRUD + auto-seed holidays
│   │   └── fees.py               # /api/fees — Razorpay order create/verify
│   ├── services/
│   │   ├── vritukul_client.py    # thin HTTP wrapper around Vritukul's API
│   │   ├── cloudinary_client.py  # CCS's own Cloudinary account
│   │   ├── docx_convert.py       # CloudConvert wrapper
│   │   ├── calendar_matcher.py   # matches notice prompts to calendar events
│   │   ├── groq_client.py        # AI notice draft generation
│   │   ├── notice_renderer.py    # renders final notice text to PDF
│   │   ├── holidays.py           # national holidays auto-seed
│   │   ├── razorpay_client.py
│   │   ├── require_admin.py      # auth/role decorators
│   │   ├── teacher_email.py      # generates teacher login emails
│   │   └── firebase_client.py    # Firebase Admin init
│   ├── models/
│   │   ├── admin_user.py
│   │   ├── teacher.py
│   │   ├── notice.py
│   │   ├── calendar_event.py
│   │   └── fee_transaction.py
│   └── static/
├── service-key.json              # Firebase service account — not committed
├── .env                          # not committed
├── requirements.txt
├── seed_official_calendar.py
├── seed_super.py
├── clean_auto_holidays.py
└── run.py
```

---

## Getting Started

### Prerequisites

- Python 3.x (see `.python-version`)
- A [Neon](https://neon.tech) Postgres database (get a connection string from your Neon project dashboard)
- Firebase project credentials (`service-key.json`) for admin auth
- Razorpay API keys
- CloudConvert API key
- Cloudinary account credentials
- Vritukul base URL + service key (for the deployed Vritukul instance)

### Setup

```bash
git clone <repo-url> ccs-backend
cd ccs-backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key

# Database (Neon)
DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<db>?sslmode=require

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# CloudConvert
CLOUDCONVERT_API_KEY=

# Razorpay
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# Vritukul (external records service)
VRITUKUL_BASE_URL=https://<vritukul-instance>.onrender.com
VRITUKUL_SERVICE_KEY=
```

Place your Firebase service account file at `service-key.json` (gitignored). Firebase init failures are logged as warnings rather than crashing the app — check `GET /health/firebase` to confirm it loaded correctly.

### Run locally

```bash
python run.py
```

The app auto-creates tables on startup (`db.create_all()`) and disables strict slashes, so trailing-slash mismatches (e.g. `/api/teachers` vs `/api/teachers/`) won't 404.

---

## Authentication & Roles

Most write/admin endpoints are protected by decorators in `services/require_admin.py`:

- `@require_admin` — verifies a Firebase ID token and attaches the user to `request.user` (`email`, `role`, `teacher_id`).
- `@require_role("super_admin")` — stacked after `@require_admin`; restricts an endpoint to a specific role.

---

## Routes Overview

| Module | Route prefix | Notes |
|---|---|---|
| Auth | `/api/auth` | Admin session info, Firebase ID token verification |
| Teachers | `/api/teachers` | Full CRUD, owned entirely by this backend, includes Firebase login creation |
| Students | `/api/students` | Search/view/edit/delete — proxied to Vritukul |
| Registers | `/api/registers` | Register file upload — proxied to Vritukul's extraction pipeline |
| Notices | `/api/notices` | Upload (PDF/DOCX → auto-converted to PDF), AI-assisted drafting, publish, delete |
| Calendar | `/api/calendar` | CRUD; national holidays auto-seeded, school events manual |
| Fees | `/api/fees` | Razorpay order create/verify — **defined but not currently registered**, see note below |

## API Reference

Base URL: `/api`

### Auth — `/api/auth`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/auth/me` | Admin | Returns the current authenticated user's email, role, teacher ID |

### Calendar — `/api/calendar`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/calendar` | Public | List events for the current academic year (Apr–Mar) |
| POST | `/calendar` | Public | Create a calendar event |
| PUT | `/calendar/<event_id>` | Public | Update a calendar event |
| DELETE | `/calendar/<event_id>` | Public | Delete a calendar event |
| POST | `/calendar/seed-holidays` | Public | Seed national holidays for a given `year` (query param) |

### Notices — `/api/notices`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/notices` | Public | List published notices |
| POST | `/notices` | Public | Upload a notice (PDF or DOCX, auto-converted) |
| GET | `/notices/<notice_id>/download` | Public | Stream the notice PDF |
| DELETE | `/notices/<notice_id>` | Public | Delete a notice |
| POST | `/notices/generate-draft` | Public | AI-match a prompt to calendar events and pre-fill notice fields |
| POST | `/notices/generate-draft/confirm` | Public | Generate draft notice text from confirmed fields |
| POST | `/notices/finalize` | Public | Render final text to PDF, upload, and save the notice |

### Fees — `/api/fees`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/fees/create-order` | Public | Create a Razorpay order for a student's fee payment |
| POST | `/fees/verify` | Public | Verify Razorpay payment signature |
| GET | `/fees` | Admin (super_admin) | List all fee transactions |

> **Note:** the `fees` blueprint is defined in `app/routes/fees.py` but is **not currently registered** in `create_app()` (`app/__init__.py`) — add `app.register_blueprint(fees_bp)` to activate these routes.

### Registers — `/api/registers`
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/registers/upload` | Admin | Upload an attendance register file for processing via Vritukul |

### Students — `/api/students`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/students/search?q=` | Admin | Search students |
| GET | `/students/sr/<sr_number>` | Admin | Get a student by SR number |
| PATCH | `/students/sr/<sr_number>` | Admin | Update a student |
| GET | `/students/list` | Admin | List all students |
| POST | `/students/create` | Admin | Create a student |
| DELETE | `/students/id/<student_id>` | Admin (super_admin) | Delete a student |
| POST | `/students/delete-bulk` | Admin (super_admin) | Bulk delete students by ID |
| POST | `/students/dedupe` | Admin (super_admin) | Find/remove duplicate student records (`dry_run` query param) |

### Teachers — `/api/teachers`
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/teachers/` | Admin (super_admin) | List all teachers (internal roster, including inactive) |
| POST | `/teachers/` | Admin (super_admin) | Create a teacher + Firebase login + AdminUser record |
| PUT | `/teachers/<teacher_id>` | Admin (super_admin) | Update a teacher |
| DELETE | `/teachers/<teacher_id>` | Admin (super_admin) | Delete a teacher and its Firebase login |

### Meta
| Method | Path | Description |
|---|---|---|
| GET | `/` | API status + auto-generated list of all registered routes |
| GET | `/health/firebase` | Firebase Admin initialization status |

---

## Data Models

All models live in `app/models/` and are registered in `app/models/__init__.py`. Note: `AdminUser` is not currently imported there, even though it's used throughout `require_admin.py` and `routes/teachers.py` — worth adding if you rely on `db.create_all()` to pick it up from a fresh database.

### AdminUser — `admin_users`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `email` | String(150), unique, required | Must match the Firebase auth email |
| `role` | String(20), required | `super_admin` \| `teacher` (default `teacher`) |
| `teacher_id` | Integer, FK → `teachers.id` | Nullable — links to a public teacher profile, if any |
| `created_at` | DateTime | |

### Teacher — `teachers`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `name` | String(150), required | |
| `subject` | String(100) | |
| `grade_level` | String(50) | |
| `bio` | Text | |
| `photo_url` | String(500) | |
| `display_order` | Integer | Default `0` — controls public sort order |
| `published` | Boolean | Default `True` |
| `created_at` | DateTime | |

### CalendarEvent — `calendar_events`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `title` | String(200), required | |
| `start_date` | Date, required | |
| `end_date` | Date | Nullable — `null` means single-day event |
| `type` | String(50), required | `Holiday` / `Exam` / `Event` / `PTM` (default `Event`) |
| `source` | String(20), required | `manual` \| `auto` (default `manual`) — `auto` = seeded via `services/holidays.py` |
| `created_at` | DateTime | |

### Notice — `notices`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `title` | String(200), required | |
| `file_url` | String(500), required | Cloudinary-hosted PDF URL |
| `original_filename` | String(200) | |
| `published` | Boolean | Default `True` |
| `uploaded_at` | DateTime | |

### FeeTransaction — `fee_transactions`
| Column | Type | Notes |
|---|---|---|
| `id` | Integer, PK | |
| `student_digital_id` | String(50), required | |
| `amount_paise` | Integer, required | Stored in paise; `to_dict()` divides by 100 for rupees |
| `razorpay_order_id` | String(100), required | |
| `razorpay_payment_id` | String(100) | Set once payment is verified |
| `status` | String(20) | `created` / `paid` / `failed` (default `created`) |
| `created_at` | DateTime | |

---

## Deployment

Deployed on **Render**. Set all environment variables listed above (plus the Firebase service account, provided as a file or as JSON in an env var depending on your Render setup) in the Render dashboard, and point the start command at `run.py` (or a WSGI entrypoint such as `gunicorn "app:create_app()"`).

## Utility Scripts

| Script | Purpose |
|---|---|
| `seed_official_calendar.py` | Seeds official school calendar events |
| `seed_super.py` | Seeds a super admin user |
| `clean_auto_holidays.py` | Removes auto-seeded holiday entries |

---

## Internal Dev Notes

- This repo and the frontend repo are separate, with independent deploys (backend → Render, frontend → Vercel), independent env vars, and independent CI.
- Do not add Vritukul as a submodule or otherwise pull its code into this repo — it's an external HTTP dependency, called the same way we'd call Razorpay or CloudConvert.
- This is a private school ERP/workbase system — credentials, `.env`, and `service-key.json` must never be committed or shared outside the team.
- `fees_bp` needs to be wired into `create_app()` before fee payment endpoints go live (see note in the API Reference above).