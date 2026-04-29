# Enverga Arena - Backend Presentation Script & Keywords

## Part 1: Project Overview (Opening)

### What is Enverga Arena?
- **Intramurals Management Platform** for Manuel S. Enverga University Foundation (MSEUF)
- Comprehensive system for **registration**, **results tracking**, **medal tallying**, and **AI-powered news recaps**
- Bridges **public viewers**, **student applicants**, **department representatives**, and **admin coordinators**

### Key Problem it Solves
- Centralized event scheduling and venue management
- Verified student tryout applications without full authentication
- Real-time results and medal standings
- AI-assisted news generation and recap publishing
- Role-based access for different user groups

---

## Part 2: Technology Stack

### Core Framework
- **Django 6.0.4** – Python web framework
- **Django REST Framework (DRF) 3.17.1** – RESTful API development
- **Python 3.14** – Runtime

### Authentication & Security
- **djangorestframework-simplejwt 5.5.1** – JWT token management
  - Access token stored in frontend memory
  - Refresh token stored as HttpOnly cookie (secure)
  - Automatic token rotation on refresh
- **PyJWT 2.12.1** – JWT handling

### API Features
- **django-cors-headers 4.9.0** – Cross-origin requests for React frontend
- **Turnstile Integration** – Bot protection on public forms

### AI & External Services
- **google-genai 1.53.0** – Gemini API for AI recaps and Rooney chatbot
- **Brevo** – Email service for OTP delivery

### Database
- **SQLite** (development) at `backend/db.sqlite3`
- **PostgreSQL driver** (psycopg2-binary 2.9.12) – Production ready

---

## Part 3: Backend Architecture & Module Structure

### Modular Monolith Pattern
```
Single Django service
      ↓
One SQLite/PostgreSQL database
      ↓
React SPA (frontend)
      ↓
External services (Gemini, Brevo, Turnstile)
```

### Four Core Django Apps (Bounded Contexts)

#### **1. Core App** – Identity & Reference Data
- **Departments**: 10 participating colleges
- **Venues & Venue Areas**: Scheduling locations with capacity tracking
- **User Profiles**: Linked to Django User model
  - Role: `admin` or `department_rep`
  - Department FK for representatives
- **News Articles**: Official published content
- **Auth Helpers**: Cookie-based JWT utilities

#### **2. Events App** – Competition Catalog
- **Event Categories**: Sport types (Basketball, Volleyball, etc.)
- **Event Definitions**: Individual competition records
  - Result modes: `match_based` or `rank_based`
  - Metadata: rules, constraints, status
  - Archive capability for past seasons

#### **3. Tournaments App** – Operations Hub
- **Schedules**: Event slot assignments with venue-area conflict validation
- **Athletes & Rosters**: Participant records and team composition
- **OTP & Tryout Applications**: Verified public registration flow
  - Email domain enforcement: `@student.mseuf.edu.ph`
  - Server-side Turnstile verification
  - Email OTP verification
- **Event Registrations**: Department roster submissions + admin approval/revision
- **Results Recording**: Match-based and rank-based result entry
- **Medal Records**: Individual awards (Gold, Silver, Bronze)
- **Medal Tally**: Derived/aggregated standings

#### **4. Rooney App** – AI & Automation
- **Query Logging**: Audit trail for all Rooney questions
- **Grounding**: Context generation from authoritative DB records
- **Gemini Integration**: LLM calls with template fallback
- **AI Recap Workflow**: Draft → Review → Approve/Discard → Publish as NewsArticle

---

## Part 4: Authentication Flow

### Login Process
- User submits credentials
- Backend returns:
  - ✅ **Access Token** (in JSON response body) – for immediate use
  - ✅ **Refresh Token** (in HttpOnly cookie) – secure, never exposed to JS
- Frontend stores access token in memory (destroyed on refresh)

### Session Restore (Page Reload)
```
Browser reloads → Frontend calls /api/auth/refresh/ 
→ HttpOnly cookie automatically sent with request 
→ New access token returned 
→ Session restored
```

### Logout
- HttpOnly cookie is cleared on backend
- In-memory access token cleared on frontend
- Session fully terminated

### JWT Claims
- **Access Token**: Contains `role` and `department` claims for authorization
- **Refresh Token**: Used only for obtaining new access tokens

---

## Part 5: Data Model & Key Entities

### Department-Centric Design
- Departments own athletes, tryout applications, registrations, medal records
- Department representatives have scoped dashboard access
- Admin has full cross-department visibility

### Result Recording (Dual Modes)
1. **Match-Based Results**
   - Head-to-head competitions (volleyball, basketball)
   - Scores and match details tracked
   - Winner determines medal

2. **Rank-Based Results**
   - Ranking/placement results (track & field, individual events)
   - Direct placement → medal assignment
   - No score calculation needed

### Medal System
- **MedalRecord**: Individual awards (gold, silver, bronze)
- **Medal Tally**: Aggregated standings per department
- **Not point-based**: Only medal counts matter
- **Olympic-style**: Derived from actual MedalRecord entries

### Venue & Schedule Management
- Venues have multiple VenueAreas (courts, fields)
- EventSchedules use venue-area slots
- **Conflict validation**: No double-booking of venue-areas
- Supports public tryout scheduling

---

## Part 6: Core API Flows

### Public Tryout Application
```
1. Student lands on public form
2. Cloudflare Turnstile challenge (bot protection)
3. Enter name, email (must be @student.mseuf.edu.ph)
4. Backend sends OTP to email
5. Student verifies OTP
6. TryoutApplication created (pending review)
7. Department representative reviews
8. Approved → Athlete record created
9. Athlete added to roster for official registration
```

### Department Registration Workflow
```
1. Department rep builds roster (adds approved athletes)
2. Submits EventRegistration for an event
3. Admin receives registration in approval queue
4. Admin reviews, approves or requests revision
5. Status tracked (pending, approved, rejected)
```

### Results & Medal Flow
```
1. Match/Competition occurs
2. Official enters results (match scores or placements)
3. MedalRecords generated automatically
4. Medal tally updated
5. Leaderboard recalculated
6. Public and admin dashboards reflect changes in real-time
```

### AI Recap Publishing
```
1. Admin triggers AI recap generation for event/schedule
2. Gemini generates draft recap with system grounding
3. Draft appears in review desk
4. Admin approves or discards
5. Approved recap published as NewsArticle
6. Public sees news in feed and on detail pages
7. Rooney query log records the event
```

---

## Part 7: API Endpoints & Route Structure

### Main URL Router
- `backend/urls.py`: Central route registration
- Uses DRF routers for auto-generated CRUD endpoints
- Auth endpoints: `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/logout/`
- Public tryout: `/api/tryouts/`
- Rooney: `/api/rooney/query/`, `/api/rooney/logs/`
- Admin: `/api/admin/recaps/`, `/api/admin/news/`

### Permission Strategy
- **Default**: `AllowAny` (public endpoints safe by design)
- **Per-View**: Tightened with authentication and role checks
- **Department-Scoped**: Representatives only see their department data
- **Admin-Only**: Sports coordination, recap review, audit logs

---

## Part 8: Database & ORM

### Django ORM Models
- Each app has `models.py` defining entities
- Relationships via Foreign Keys and Many-to-Many
- Migrations managed via `manage.py migrate`
- Currently: 2 migration batches committed (initial, menu descriptions in v1 legacy)

### Query Optimization
- Serializers handle data transformation
- Select/prefetch related for N+1 prevention
- Filtering via DRF filter backends

### Data Integrity
- Foreign key constraints prevent orphaned records
- Venue-area conflict validation in schedule creation
- Email domain enforcement in tryout applications
- Result mode validation (match vs rank)

---

## Part 9: Environment Configuration

### `.env` Variables
Located: `backend/.env.example`

**Key Variables:**
- `SECRET_KEY`: Django security key
- `DEBUG`: Development mode toggle
- `ALLOWED_HOSTS`: CORS and request validation
- `DATABASE_URL`: PostgreSQL connection string (future)
- `CORS_ALLOWED_ORIGINS`: Frontend URL for cross-origin requests
- `JWT_ALGORITHM`: Token signing (default: HS256)
- `REFRESH_TOKEN_COOKIE_SECURE`, `REFRESH_TOKEN_COOKIE_HTTPONLY`: Cookie security
- `GEMINI_API_KEY`: Google API key for AI features
- `TURNSTILE_SECRET_KEY`: Cloudflare verification
- `EMAIL_BACKEND`, `EMAIL_HOST`, `BREVO_API_KEY`: Email service config

### Bootstrapping
```
1. Python venv activated
2. pip install -r requirements.txt
3. Configure .env (copy from .env.example)
4. python manage.py migrate
5. python manage.py runserver
```

---

## Part 10: Quality Attributes & Priorities

### 1. **Correctness** (Highest)
- Official results and standings must be accurate
- Validation at serializer and service layer
- No concurrent result overwrites

### 2. **Role-Based Data Segregation**
- Department reps only see their department
- Admins see all, can filter
- Public sees published news and public leaderboards

### 3. **Auditability**
- Rooney query logs track every AI question + response
- AI recap history: draft → review → publish
- News article audit trail

### 4. **Operational Usability**
- Admin dashboard with KPIs and quick actions
- Department rep workflow streamlined for roster building
- Public tryout process: self-service, verified

### 5. **Fast Demo Iteration**
- SQLite for quick development
- Modular apps allow testing individual features
- Seed data scripts for demo purposes

---

## Part 11: Key Architectural Decisions

### Decision 1: Result Family Split (Match vs Rank)
- **Why**: Different sports have different result formats
- **Impact**: Separate result models, but unified medal system
- **Trade-off**: More complex validation, but cleaner per-sport logic

### Decision 2: Medal Standing from MedalRecords
- **Why**: Atomic truth source, no points/scoring ambiguity
- **Impact**: Tally is always derived, never out of sync
- **Trade-off**: Must regenerate tally on result changes

### Decision 3: JWT in Memory + HttpOnly Cookie
- **Why**: Security (HttpOnly prevents XSS token theft) + UX (auto-refresh on page reload)
- **Impact**: Hybrid auth strategy, immune to most token attacks
- **Trade-off**: CSRF less applicable with API-based frontend

### Decision 4: Public Tryouts = No Student Accounts
- **Why**: Lower barrier to entry, reduce account bloat
- **Impact**: Email OTP verification instead of username/password
- **Trade-off**: Lost account history per student, but no credential management

### Decision 5: Rooney Context = Server-Generated
- **Why**: Consistent, authoritative grounding from DB
- **Impact**: All Rooney responses reflect official data
- **Trade-off**: Regenerate context on each query (performance cost worth correctness)

### Decision 6: AI Recaps = Internal Drafts Until Publishing
- **Why**: Admin review gate ensures quality before public visibility
- **Impact**: Two-phase workflow: generation → approval → news publish
- **Trade-off**: Latency between event and public news

---

## Part 12: Current Limitations & Out of Scope

### Not Yet Implemented
- ❌ **Student Login Accounts**: Currently public tryout only
- ❌ **Payment / Billing**: No transaction tracking
- ❌ **Multi-Tenant**: Single university only
- ❌ **Production Deployment**: No IaC, limited observability
- ❌ **Asynchronous Tasks**: AI/email run synchronously
- ❌ **Full Observability**: No metrics, distributed tracing, centralized logs

### Known Constraints
- **SQLite in Dev**: Auto-switches to PostgreSQL in production settings ready
- **Default AllowAny**: Must tighten per-view for security
- **Synchronous AI Calls**: May timeout on slow LLM responses
- **Email Delivery**: Requires Brevo API key and configuration

---

## Part 13: Deployment & Operations

### Development
```bash
cd backend
source ../venvv/bin/activate
python manage.py runserver
# API available at http://localhost:8000
```

### Production Readiness
- PostgreSQL driver installed (swap SQLite → DATABASE_URL)
- CORS headers properly configured
- JWT rotation strategy enabled
- HttpOnly cookie security flags set
- Environment-driven settings (no hardcoding)

### Admin Operations
- **Dashboard**: Real-time KPIs, registration queue, schedule overview
- **Audit Logs**: Rooney queries, news publication, registration changes
- **Data Management**: Bulk actions (tally verification, result fixes)
- **Configuration**: Add venues, events, categories without code changes

---

## Part 14: Future Enhancements

### Roadmap Ideas
- ✨ Real-time notifications (WebSocket for live results)
- ✨ Mobile app (same API backend)
- ✨ Advanced AI: Sentiment analysis on news comments
- ✨ Analytics: Participation trends, gender metrics, dept performance over years
- ✨ Payment Integration: Merchandise shop
- ✨ Async Queue: Celery for AI/email jobs
- ✨ Multi-Tenant: Multiple universities on one platform

---

## Part 15: Presenter Talking Points (Q&A Prep)

### "Why Django for this project?"
- **Answer**: Rapid development, ORM handles complex queries, DRF excellent for APIs, built-in admin panel for operations, large ecosystem, team familiarity

### "How do you ensure data integrity?"
- **Answer**: Serializer validation, database constraints, conflict checks on schedules, immutable audit logs, two-phase AI recap approval

### "What if Gemini API fails?"
- **Answer**: Fallback to template-based recap generation, query still logged, draft still created, admin can publish template version

### "How is the system secure?"
- **Answer**: JWT with HttpOnly cookies, role-based access control, email OTP for tryouts, Turnstile bot protection, HTTPS-enforced (production), CORS whitelisting

### "Can it scale?"
- **Answer**: Modular monolith can split apps into microservices later, PostgreSQL supports larger datasets, can add caching layer, async task queue (Celery) ready

### "What about concurrent result entries?"
- **Answer**: Database-level locks on result records, serializer validation catches duplicates, admin review process minimizes manual overwrites

---

## Part 16: Demo Flow (Live Walkthrough)

### 1. Public Site
- "Here's the home page... hero section, current leaders podium..."
- Click on "Leaderboard" → Show medal tally, filter by department
- Click on "News" → Show published articles (derived from AI recaps)

### 2. Tryout Application (Public)
- "No login needed... just email and OTP..."
- Fill form, show Turnstile, verify email
- "After approval by dept rep, they become an athlete"

### 3. Admin Dashboard
- "Sports coordinator sees all departments, registrations pending..."
- Show KPI cards: total participants, pending approvals, schedule conflicts
- Navigate to event creation, show result mode options

### 4. Department Rep Portal
- "Scoped to their department... roster building, status tracking..."
- Add athlete to roster, submit registration
- Show response: "Awaiting admin approval"

### 5. Results & Tally
- "Official enters results... medal records auto-generated..."
- Leaderboard updates in real-time
- Show medal count change for winning department

### 6. AI Recap & Rooney
- "Admin triggers AI recap for an event..."
- Show draft recap in review desk
- Approve → Published as news article
- Show "Ask Rooney" chatbot using grounded data

---

## Part 17: Code Organization Summary

```
backend/
├── manage.py                 # Django CLI
├── requirements.txt          # Python dependencies
├── .env.example              # Config template
├── db.sqlite3                # Dev database
│
├── backend/                  # Project settings
│   ├── settings.py           # Django configuration
│   ├── urls.py               # Route registration
│   ├── asgi.py / wsgi.py     # App servers
│
├── core/                     # Identity & reference
│   ├── models.py             # User, Department, Venue, News
│   ├── views.py / serializers.py
│   └── urls.py
│
├── events/                   # Competition catalog
│   ├── models.py             # EventCategory, Event
│   ├── views.py / serializers.py
│   └── urls.py
│
├── tournaments/              # Operations hub
│   ├── models.py             # Schedule, Athlete, Result, Medal
│   ├── views.py / serializers.py
│   ├── services.py           # Business logic
│   ├── api_urls.py / api_views.py
│   └── migrations/
│
└── rooney/                   # AI & recaps
    ├── models.py             # RooneyQuery, AIRecap
    ├── views.py / serializers.py
    └── services.py           # Gemini integration
```

---

## Summary Slide

**Enverga Arena Backend = Smart, Modular Sports Management**

| Aspect | Highlight |
|--------|-----------|
| **Stack** | Django + DRF + Gemini AI |
| **Architecture** | Modular monolith, 4 bounded contexts |
| **Auth** | JWT + HttpOnly cookies, role-based |
| **Data** | Relational (PostgreSQL-ready), derived tally |
| **AI** | Grounded Rooney Q&A, admin-reviewed recaps |
| **Security** | OTP verification, Turnstile, CORS, encrypted cookies |
| **Quality** | Correctness > Scalability > Operations > DX |

**Questions?**
