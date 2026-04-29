# Enverga Arena

**Intramurals Registration, Results, and Medal Tally System with AI News Recap** for Manuel S. Enverga University Foundation (MSEUF).

Enverga Arena is a web application for public intramurals viewing, verified student tryout applications, department-representative operations, admin sports coordination, official news, Rooney AI, and admin-reviewed AI recap publishing.

## Current Feature Set

- **Public Site**
  - Home page with hero, current leaders podium, and latest published news
  - Public schedules
  - Public results, medal tally, and leaderboard
  - Published news and full article pages
  - Rooney AI assistant grounded in official data
  - Public verified tryout application form

- **Authentication**
  - Access JWT is stored in frontend memory only
  - Refresh JWT is stored in a backend-issued HttpOnly cookie
  - Session restore after page reload uses `/api/auth/refresh/`
  - Logout clears the refresh cookie and in-memory auth state

- **Admin / Sports Coordinator**
  - Dashboard with KPIs, registrations, schedules, leaderboard snapshot, Rooney preview, and quick actions
  - Department, venue, category, event, and schedule management
  - Event create/edit/archive with metadata and linked-record safeguards
  - Schedule create/edit with venue-area conflict awareness
  - Registration review and approval/revision workflow
  - Participant management
  - Results entry review surface
  - Medal tally and leaderboard verification
  - News management
  - AI recap review desk
  - Rooney query log monitoring

- **Department Representative**
  - One representative account per department
  - Department-scoped dashboard
  - Verified tryout application review
  - Selected applicant conversion into athlete records
  - Participant/athlete management
  - Roster building and official registration submission
  - Registration status tracking
  - Department schedule, results, medal summary, news, and Rooney access

- **Public Tryout Flow**
  - No student accounts in v1
  - Cloudflare Turnstile challenge on the client
  - Server-side Turnstile verification
  - Student email domain enforcement: `@student.mseuf.edu.ph`
  - Brevo transactional email OTP
  - Hashed OTP storage
  - Rate limiting and duplicate protection

- **News and AI Recap**
  - `NewsArticle` is official public content
  - `AIRecap` is internal/admin-only draft content
  - Result finalization can generate grounded recap drafts
  - Admin reviews/edits/approves/discards/publishes recaps
  - Published recaps become official public news

- **Medal Ranking**
  - Olympic-style medal priority only
  - Gold descending, then silver, then bronze, then department name
  - No points system
  - Total medals are shown only as context

## Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** Django + Django REST Framework
- **Database:** SQLite for local/dev in current settings; PostgreSQL driver installed for production direction
- **Styling:** Tailwind CSS + DaisyUI
- **HTTP client:** Axios
- **Server state:** TanStack React Query
- **AI:** Google GenAI SDK with Gemini model chain
- **Bot protection:** Cloudflare Turnstile
- **Transactional email:** Brevo

## Package Inventory

### Backend Python Packages

From `backend/requirements.txt`:

- `asgiref==3.11.1`
- `Django==6.0.4`
- `django-cors-headers==4.9.0`
- `djangorestframework==3.17.1`
- `djangorestframework_simplejwt==5.5.1`
- `google-genai==1.53.0`
- `psycopg2-binary==2.9.12`
- `PyJWT==2.12.1`
- `python-dotenv==1.2.2`
- `sqlparse==0.5.5`

### Frontend Runtime Packages

From `frontend/package.json`:

- `@tanstack/react-query@^5.100.1`
- `axios@^1.15.2`
- `date-fns@^4.1.0`
- `jwt-decode@^4.0.0`
- `lucide-react@^1.9.0`
- `react@^19.2.5`
- `react-dom@^19.2.5`
- `react-router-dom@^7.14.2`

### Frontend Development Packages

From `frontend/package.json`:

- `@eslint/js@^10.0.1`
- `@tailwindcss/vite@^4.2.4`
- `@types/node@^24.12.2`
- `@types/react@^19.2.14`
- `@types/react-dom@^19.2.3`
- `@vitejs/plugin-react@^6.0.1`
- `daisyui@^5.5.19`
- `eslint@^10.2.1`
- `eslint-plugin-react-hooks@^7.1.1`
- `eslint-plugin-react-refresh@^0.5.2`
- `globals@^17.5.0`
- `tailwindcss@^4.2.4`
- `typescript@~6.0.2`
- `typescript-eslint@^8.58.2`
- `vite@^8.0.10`

## Local Setup

### 1. Backend

Create and activate a virtual environment at the project root:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Create backend env file:

```bash
copy .env.example .env
```

Fill in required values in `backend/.env`.

For local demo without real AI/email submissions, placeholders can remain for external services, but real tryout OTP and Gemini responses require:

- `GEMINI_API_KEY`
- `TURNSTILE_SECRET_KEY`
- `BREVO_API_KEY`
- `BREVO_SENDER_EMAIL`
- `BREVO_SENDER_NAME`

Run migrations and seed demo data:

```bash
python manage.py migrate
python manage.py seed_data
```

Start backend:

```bash
python manage.py runserver
```

Backend runs at `http://localhost:8000`.

### 2. Frontend

Install dependencies:

```bash
cd frontend
npm install
```

Create frontend env file:

```bash
copy .env.example .env
```

Set safe public values:

```env
VITE_API_URL=http://localhost:8000/api
VITE_TURNSTILE_SITE_KEY=your_turnstile_site_key_here
```

Start frontend:

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Demo Accounts

Created by `python manage.py seed_data`:

- Admin / Sports Coordinator: `admin` / `demo1234`
- Department reps:
  - `cafa_rep`
  - `cas_rep`
  - `cba_rep`
  - `ccms_rep`
  - `ccjc_rep`
  - `ced_rep`
  - `ceng_rep`
  - `cihtm_rep`
  - `cme_rep`
  - `cnahs_rep`
- Department rep password: `demo1234`
- Public viewer: no account required
- Student applicants: no account in v1; they apply through `/tryouts`

## Main Routes

### Public

- `/`
- `/news`
- `/schedules`
- `/results`
- `/rooney`
- `/tryouts`
- `/login`

### Admin

- `/admin`
- `/admin/departments`
- `/admin/venues`
- `/admin/categories`
- `/admin/events`
- `/admin/schedules`
- `/admin/registrations`
- `/admin/participants`
- `/admin/results-entry`
- `/admin/medal-tally`
- `/admin/leaderboard`
- `/admin/news`
- `/admin/ai-recaps`
- `/admin/rooney-logs`
- `/admin/settings`

### Department Representative

- `/portal`
- `/portal/summary`
- `/portal/tryouts`
- `/portal/selected-applicants`
- `/portal/masterlist`
- `/portal/events`
- `/portal/rosters`
- `/portal/registration-status`
- `/portal/schedules`
- `/portal/results`
- `/portal/medals`
- `/portal/news`
- `/portal/rooney`

## API Overview

Base URL: `http://localhost:8000/api`

### Auth

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

### Public Tryouts

- `POST /api/public/tryouts/send-otp/`
- `POST /api/public/tryouts/verify-otp/`
- `POST /api/public/tryouts/apply/`

### Public/Router Endpoints

- `/api/public/departments/`
- `/api/public/venues/`
- `/api/public/venue-areas/`
- `/api/public/event-categories/`
- `/api/public/events/`
- `/api/public/schedules/`
- `/api/public/athletes/`
- `/api/public/tryout-applications/`
- `/api/public/registrations/`
- `/api/public/match-results/`
- `/api/public/podium-results/`
- `/api/public/medal-records/`
- `/api/public/medal-tally/`
- `/api/public/news/`
- `/api/public/rooney-logs/`
- `POST /api/public/rooney/query/`

Some endpoints under `/api/public/` are public-read but protected for writes.

### Admin

- `/api/admin/news/`
- `/api/admin/ai-recaps/`
- `/api/admin/ai-recaps/generate/`
- `/api/admin/ai-recaps/{id}/approve/`
- `/api/admin/ai-recaps/{id}/discard/`
- `/api/admin/ai-recaps/{id}/publish/`

## Verification Commands

Backend:

```bash
cd backend
python manage.py check
python manage.py test
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

On Windows in this Codex sandbox, `npm run build` may need to run outside the sandbox because Tailwind's native `@tailwindcss/oxide-win32-x64-msvc` module can hit `spawn EPERM`. The build itself passes when run normally.

## Architecture Docs

Detailed docs live in [architecture/](./architecture/):

- system overview
- backend architecture
- frontend architecture
- data model
- API contracts
- runtime flows
- deployment and operations
- security/testing/risks
- decisions and roadmap

Additional technical docs:

- [Authentication docs](./docs/auth/)
- [API testing guide](./docs/api-testing/)

## Important Demo Notes

- Rotate any real secrets that were ever committed or shared before a real demo.
- The current dev database is SQLite.
- PostgreSQL is the intended production direction but is not wired in settings yet.
- Rooney and AI recaps can fall back or refuse gracefully when Gemini is not configured.
- Real tryout OTP sending requires valid Turnstile and Brevo credentials.

## License

Internal academic project.
