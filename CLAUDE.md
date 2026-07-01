# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Ride Tracker: personal fullstack app to log remis (taxi) trips with weekly financial tracking. UI is entirely in Spanish, single-user (no public registration).

## Commands

### Backend (from `backend/`)

```bash
# Setup
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt   # Windows
copy .env.example .env                            # then edit values
python seed.py                                     # creates the initial user

# Run dev server (Windows, from repo root)
& "backend\venv\Scripts\uvicorn.exe" --app-dir backend app.main:app --reload --port 8000

# Tests (30 total: auth 6, trips 10, weeks 14)
.\venv\Scripts\python -m pytest tests/ -v
.\venv\Scripts\python -m pytest tests/test_trips.py -v      # single file
.\venv\Scripts\python -m pytest tests/test_trips.py::test_name -v  # single test
```

Tests use a separate SQLite file (`test_ride_tracker.db`) and reduce bcrypt to 4 rounds for speed (see `backend/tests/conftest.py`). `DATABASE_URL` and `SECRET_KEY` are set via `os.environ.setdefault` before the app is imported, so no `.env` is required to run tests.

### Frontend (from `frontend/`)

```bash
npm install
copy .env.example .env    # set PUBLIC_API_URL=http://localhost:8000
npm run dev                # http://localhost:4321
npm run build               # static output to dist/, verify before deploy
```

There is no frontend test suite or linter configured.

## Architecture

### Backend — layered FastAPI app (`backend/app/`)

Request flow: `routes/` → `services/` → `repositories/` → `models/` (SQLAlchemy). `schemas/` holds Pydantic I/O models, kept separate from ORM models.

- `config.py` — Pydantic settings loaded from `.env`. `DATABASE_URL` starting with `mysql://` is auto-rewritten to `mysql+pymysql://` (Railway quirk).
- `database.py` — engine/session/`Base`, `init_db()` (called in the FastAPI `lifespan`, creates tables — no migration tool).
- `services/week_service.py` — the core business rule: weeks run **Wednesday → Tuesday**, payment date is `week_start + 9 days` (the following Friday). `get_week_start` computes the Wednesday on/before a given date via `(weekday - 2) % 7`. Any date/week logic must go through these helpers — don't recompute week boundaries inline.
- `services/trip_service.py` — pricing logic: individual trip = $30.00; paired trip = $25.00/person = $50.00 total (see `models/trip.py` `TripType` enum).
- `utils/security.py` — JWT create/decode (python-jose) and bcrypt hashing (passlib).
- `utils/dependencies.py` — `get_current_user` FastAPI dependency; it accepts the JWT from **either** an `Authorization: Bearer` header **or** the `access_token` cookie (header takes precedence). `/auth/login` both returns the token in the JSON body and sets it as an HTTP-only cookie.
- The frontend (`lib/api.js`) actually authenticates with the **Bearer header**: it stores the token from the login response in `localStorage` (`rt_token`) and sends it on every request. The cookie path exists on the backend but the frontend does not rely on it (`credentials: 'include'` is not set).
- Auth cookie flags depend on `settings.PRODUCTION`: in production the cookie is set with `Secure=True, SameSite=none` (needed for the cross-domain Vercel↔Railway setup); in dev it is `Secure=False, SameSite=lax`.

### Frontend — Astro (static output) + Vue islands (`frontend/src/`)

- Pages (`pages/*.astro`) are static shells; interactive pieces are Vue SFCs (`components/*.vue`) hydrated as islands.
- `layouts/MainLayout.astro` handles the header/nav and the auth guard (redirects to `/login` when unauthenticated).
- `lib/api.js` — fetch wrapper; stores the JWT from login in `localStorage` (`rt_token`) and sends it as an `Authorization: Bearer` header on every request. On a `401` it clears the token and redirects to `/login`.
- `lib/dates.js` — frontend mirror of the week/payment-date logic; must stay consistent with `backend/app/services/week_service.py` if that logic ever changes.

### Deploy topology

Frontend on Vercel (root dir `frontend`, static `dist/`), backend on Railway (`Procfile` + `railway.json`, health check at `/health`). Production DB is MySQL (Railway plugin); local dev DB is SQLite. Full deploy/runbook detail (CORS setup, seeding on Railway, password reset) lives in `DEPLOY.md` — consult it before making deploy-related changes rather than duplicating it here.
