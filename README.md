# Personal Job Application Portal

Local-first job-search automation for one person. It collects jobs from configured APIs, scores them against your profile, tracks the application pipeline, generates ATS-friendly `.docx` resumes and cover letters, and includes a Chrome companion for saving LinkedIn, Indeed, Glassdoor, and Handshake pages without scraping them.

## What I tightened from the original prompt

The original brief was good, but too large to build honestly in one pass. This scaffold keeps the same destination while separating real local workflows from integration-dependent workflows:

- API aggregators are opt-in by env key. Missing keys produce empty results instead of fake jobs.
- LinkedIn, Glassdoor, and Handshake are handled through the extension/manual capture flow only.
- OpenAI calls have deterministic fallbacks, so the app still runs before you add `OPENAI_API_KEY`.
- Gmail is represented by a stable worker contract, with OAuth wiring documented as the next integration step.
- The first app surface is the actual dashboard, not a marketing page.

## Stack

- Backend: FastAPI, SQLAlchemy 2, Alembic, Celery, Redis, PostgreSQL
- Frontend: Next.js 14 App Router, TypeScript strict mode, Tailwind, lucide icons
- Documents: `python-docx`
- Extension: Chrome MV3
- Runtime: Docker Compose

## Setup

1. Copy environment defaults:

   ```bash
   cp .env.example .env
   ```

2. Fill keys as needed. The app can start without aggregator or OpenAI keys, but live pulls need provider keys.

3. Start the stack:

   ```bash
   docker compose up --build
   ```

4. Seed local demo data:

   ```bash
   docker compose exec backend python -m scripts.seed
   ```

5. Open:

   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

## Core API

- `PUT /api/profile` saves the single-user resume/profile/preferences.
- `POST /api/jobs/ingest` pulls configured providers and scores jobs.
- `POST /api/jobs/capture-url` stores a manually captured job URL.
- `POST /api/applications` saves or marks a job.
- `POST /api/applications/{id}/tailor-resume` generates an ATS `.docx`.
- `POST /api/cover-letter` generates a cover letter `.docx`.
- `GET /api/analytics` returns dashboard counters.

## Chrome extension

1. Open Chrome extensions.
2. Enable Developer mode.
3. Load unpacked extension from `extension/`.
4. Visit a supported job page.
5. Click `Save to Portal`.

The extension posts extracted page text to `http://localhost:8000/api/jobs/capture-url`.

## Integration limits

- Indeed: use Publisher API or JSearch through RapidAPI.
- LinkedIn: no public job-search API. Use the extension or manual URL capture.
- Glassdoor: public API discontinued. Use the extension or manual URL capture.
- Handshake: no public API. Use the extension or manual URL capture.
- Gmail: use official Google OAuth scopes `gmail.readonly` and `gmail.modify`; worker stubs are in place.

## Next build steps

1. Add password-protected frontend auth and wire the onboarding form to `PUT /api/profile`.
2. Complete Gmail OAuth token storage and thread fetch in `backend/app/integrations/gmail.py`.
3. Add application detail pages with document download links.
4. Add Recharts pipeline charts once live data is flowing.
5. Add Google Calendar interview sync.
