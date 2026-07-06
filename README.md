# CCS Backend (capecomorin-backend)

**Private, proprietary repository.** This is the backend for the internal **Cape Comorin School (CCS)** ERP/website system — powering [capecomorinschool.com](https://capecomorinschool.com) and its admin/workbase panel at `admin.capecomorinschool.com`. Not open source; not for external distribution. Access restricted to the CCS engineering/ops team.

> Status: 🚧 In progress — core routes and DB wiring are up and running; several modules are still being built out (see [Status](#status) below).

---

## What this service is

This is the **only backend the frontend talks to.** It owns all CCS-specific logic (fees, notices, calendar, teachers, contact/admissions forms) and internally proxies to **Vritukul** (a separate, already-deployed FastAPI service) for anything records-related — students, TC (Transfer Certificate) generation, and register uploads.

```
Next.js frontend (public site + admin.capecomorinschool.com)
        ↓ (only talks to)
Flask backend (this repo)
        ↓ (proxies to, when needed)
Vritukul (FastAPI, deployed separately on Render)
```

**Key principle:** Vritukul stays completely untouched by this repo. Its entire footprint here is two env vars (`VRITUKUL_BASE_URL`, `VRITUKUL_API_KEY`) and a single client file, `app/services/vritukul_client.py`. Nothing else in this codebase needs to know it exists.

---

## Tech stack

| Area | Choice |
|---|---|
| Framework | Flask |
| Database | **Neon** (serverless Postgres) |
| Records backend | Vritukul (FastAPI, external, accessed only via proxy) |
| Auth (admin panel) | Firebase (JWT verification) |
| File storage | Cloudinary (separate account from Vritukul's) |
| Fee payment | Razorpay — test key, demo scope only for v1 |
| Notice storage | PDF/DOCX uploads; DOCX auto-converted to PDF via CloudConvert |
| Academic calendar | National holidays auto-seeded via a holidays API; school-specific entries added manually |
| Deployment | Render |

---

## Project structure

```
capecomorin-backend/
├── app/
│   ├── __init__.py               # app factory
│   ├── config.py
│   ├── extensions.py
│   ├── routes/
│   │   ├── teachers.py           # CRUD — owned entirely by this backend
│   │   ├── students.py           # calls out to Vritukul
│   │   ├── registers.py          # calls out to Vritukul
│   │   ├── notices.py            # upload, convert, list, delete
│   │   ├── calendar.py           # CRUD + auto-seed holidays
│   │   ├── fees.py               # Razorpay order create/verify (test)
│   │   ├── contact.py            # contact/admission enquiry forms
│   │   └── auth.py               # admin login/session
│   ├── services/
│   │   ├── vritukul_client.py    # thin HTTP wrapper around Vritukul's API
│   │   ├── cloudinary_client.py  # CCS's own Cloudinary account
│   │   ├── docx_convert.py       # CloudConvert wrapper
│   │   ├── holidays.py           # national holidays auto-seed
│   │   └── razorpay_client.py
│   ├── models/
│   │   ├── teacher.py
│   │   ├── notice.py
│   │   ├── calendar_event.py
│   │   └── fee_transaction.py
│   ├── db.py                     # Neon (Postgres) connection/session setup
│   └── firebase.py               # verifies admin panel JWTs
├── firebase-key.json             # not committed
├── .env                          # not committed
├── requirements.txt
└── run.py
```

---

## Getting started

### Prerequisites

- Python 3.11+
- A [Neon](https://neon.tech) Postgres database (get a connection string from your Neon project dashboard)
- Firebase project credentials (`firebase-key.json`) for admin auth
- Razorpay test API keys
- CloudConvert API key
- Cloudinary account credentials
- Vritukul base URL + API key (for the deployed Vritukul instance)

### Setup

```bash
git clone <repo-url> capecomorin-backend
cd capecomorin-backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
# Database (Neon)
DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<db>?sslmode=require

# Vritukul (external records service)
VRITUKUL_BASE_URL=https://<vritukul-instance>.onrender.com
VRITUKUL_API_KEY=

# Firebase (admin auth)
FIREBASE_CREDENTIALS_PATH=firebase-key.json

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Razorpay (test mode)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

# CloudConvert
CLOUDCONVERT_API_KEY=

# Misc
FLASK_ENV=development
```

Place your Firebase service account file at `firebase-key.json` (already gitignored).

### Run locally

```bash
flask --app run.py run --debug
```

---

## Routes overview

| Module | Route prefix | Notes |
|---|---|---|
| Auth | `/auth` | Admin login/session, Firebase JWT verification |
| Teachers | `/teachers` | Full CRUD, owned entirely by this backend |
| Students | `/students` | Search/view/edit/TC generation — proxied to Vritukul |
| Registers | `/registers` | Scanned register PDF upload — proxied to Vritukul's AI extraction pipeline |
| Notices | `/notices` | Upload (PDF/DOCX → auto-converted to PDF), publish/unpublish, delete |
| Calendar | `/calendar` | CRUD; national holidays auto-seeded, school events manual |
| Fees | `/fees` | Razorpay order create/verify (test key, demo transaction log only) |
| Contact | `/contact` | Contact + admissions enquiry form submissions |

---

## Status

- ✅ Core Flask app factory, config, and DB connection to Neon — working
- ✅ Some routes already running (confirm per-module as they land)
- 🚧 Vritukul proxy client — in progress
- 🚧 Notice upload + DOCX→PDF conversion pipeline — in progress
- 🚧 Fee payment (Razorpay test) — in progress
- ⏳ Cloudinary account (separate vs. shared with Vritukul) — to confirm
- ⏳ DOCX→PDF provider — leaning CloudConvert, not finalized

---

## Internal dev notes

- This repo and `capecomorin-frontend` are separate repos with independent deploys (backend → Render, frontend → Vercel), independent env vars, and independent CI.
- Do not add Vritukul as a submodule or otherwise pull its code into this repo — it's an external HTTP dependency, called the same way we'd call Razorpay or CloudConvert.
- UP Board affiliation is real and used internally/administratively but is intentionally not featured in public-facing marketing copy — that's a frontend content decision, not something this backend needs to enforce, just something to be aware of if building admin-facing content tools.
- This is a private school ERP/workbase system — credentials, `.env`, and `firebase-key.json` must never be committed or shared outside the team.