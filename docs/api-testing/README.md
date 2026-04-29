# Enverga Arena API Testing Guide

This guide documents how to test the current Enverga Arena API with Postman, Insomnia, Bruno, Thunder Client, or plain HTTP clients.

The route list is based on `backend/backend/urls.py`, which is the backend route source of truth.

## Quick Summary

- Local API base URL: `http://localhost:8000/api`
- All API routes use trailing slashes.
- Auth uses access JWT in the response body and refresh JWT in an HttpOnly cookie.
- Protected requests use `Authorization: Bearer {{access_token}}`.
- Refresh requests depend on the client cookie jar sending the HttpOnly refresh cookie.
- Many resources under `/api/public/` are public for reads but protected for writes.

## Recommended Postman Environment

Create a Postman environment named `Enverga Arena Local`.

| Variable | Initial Value | Notes |
| --- | --- | --- |
| `base_url` | `http://localhost:8000/api` | API base without trailing slash |
| `username` | `admin` | Seeded demo admin username if `seed_data` has run |
| `password` | `demo1234` | Seeded demo password if unchanged |
| `access_token` | empty | Filled by login/refresh test script |
| `department_id` | `1` | Replace with a real department id |
| `venue_id` | `1` | Replace after listing venues |
| `venue_area_id` | `1` | Replace after listing venue areas |
| `category_id` | `1` | Replace after listing categories |
| `event_id` | `1` | Replace after listing events |
| `schedule_id` | `1` | Replace after listing schedules |
| `athlete_id` | `1` | Replace after listing athletes |
| `registration_id` | `1` | Replace after listing registrations |
| `tryout_application_id` | `1` | Replace after listing tryout applications |
| `match_result_id` | `1` | Replace after listing match results |
| `podium_result_id` | `1` | Replace after listing podium results |
| `medal_record_id` | `1` | Replace after listing medal records |
| `medal_tally_id` | `1` | Replace after listing medal tally rows |
| `news_id` | `1` | Replace after listing admin news |
| `news_slug` | `published-update` | Replace after listing public news |
| `ai_recap_id` | `1` | Replace after listing AI recaps |
| `rooney_log_id` | `1` | Replace after listing Rooney logs |
| `turnstile_token` | empty | Required only for real public tryout OTP testing |
| `otp_code` | empty | Fill from email/log during real OTP testing |

## Postman Auth Setup

### Login

- Method: `POST`
- URL: `{{base_url}}/auth/login/`
- Body: raw JSON

```json
{
  "username": "{{username}}",
  "password": "{{password}}"
}
```

Postman `Tests` script:

```js
pm.test("Login returned access token", function () {
  pm.response.to.have.status(200);
  const json = pm.response.json();
  pm.expect(json.access).to.be.a("string");
  pm.environment.set("access_token", json.access);
});
```

The backend also sets the refresh cookie. In Postman, check `Cookies` for `localhost` and look for the configured cookie name, usually `enverga_refresh`.

### Protected Requests

Use the `Authorization` tab:

- Type: `Bearer Token`
- Token: `{{access_token}}`

Equivalent manual header:

```http
Authorization: Bearer {{access_token}}
```

### Refresh

- Method: `POST`
- URL: `{{base_url}}/auth/refresh/`
- Body: none

Postman should send the refresh cookie from its cookie jar automatically.

Postman `Tests` script:

```js
pm.test("Refresh returned access token", function () {
  pm.response.to.have.status(200);
  const json = pm.response.json();
  pm.expect(json.access).to.be.a("string");
  pm.environment.set("access_token", json.access);
});
```

### Logout

- Method: `POST`
- URL: `{{base_url}}/auth/logout/`

Postman `Tests` script:

```js
pm.test("Logged out", function () {
  pm.response.to.have.status(200);
  pm.environment.unset("access_token");
});
```

If Postman still sends an old refresh cookie after logout, clear cookies for `localhost` in Postman's cookie manager.

## Route Checklist

### Authentication

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| POST | `{{base_url}}/auth/login/` | None | `CookieTokenObtainPairView` | Login; returns access JWT and sets refresh cookie |
| POST | `{{base_url}}/auth/refresh/` | Refresh cookie | `CookieTokenRefreshView` | Returns fresh access JWT |
| POST | `{{base_url}}/auth/logout/` | None | `LogoutView` | Clears refresh cookie |
| GET | `{{base_url}}/auth/me/` | Bearer | `CurrentUserView` | Returns current user role/department payload |

### Core Reference Data

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/departments/` | None | `DepartmentViewSet` | List departments |
| POST | `{{base_url}}/public/departments/` | Admin bearer | `DepartmentViewSet` | Create department |
| GET | `{{base_url}}/public/departments/{{department_id}}/` | None | `DepartmentViewSet` | Get department detail |
| PUT/PATCH | `{{base_url}}/public/departments/{{department_id}}/` | Admin bearer | `DepartmentViewSet` | Update department |
| DELETE | `{{base_url}}/public/departments/{{department_id}}/` | Admin bearer | `DepartmentViewSet` | Delete department |
| GET | `{{base_url}}/public/venues/` | None | `VenueViewSet` | List venues |
| POST | `{{base_url}}/public/venues/` | Admin bearer | `VenueViewSet` | Create venue |
| GET | `{{base_url}}/public/venues/{{venue_id}}/` | None | `VenueViewSet` | Get venue detail |
| PUT/PATCH | `{{base_url}}/public/venues/{{venue_id}}/` | Admin bearer | `VenueViewSet` | Update venue |
| DELETE | `{{base_url}}/public/venues/{{venue_id}}/` | Admin bearer | `VenueViewSet` | Delete venue |
| GET | `{{base_url}}/public/venue-areas/` | None | `VenueAreaViewSet` | List venue areas |
| POST | `{{base_url}}/public/venue-areas/` | Admin bearer | `VenueAreaViewSet` | Create venue area |
| GET | `{{base_url}}/public/venue-areas/{{venue_area_id}}/` | None | `VenueAreaViewSet` | Get venue area detail |
| PUT/PATCH | `{{base_url}}/public/venue-areas/{{venue_area_id}}/` | Admin bearer | `VenueAreaViewSet` | Update venue area |
| DELETE | `{{base_url}}/public/venue-areas/{{venue_area_id}}/` | Admin bearer | `VenueAreaViewSet` | Delete venue area |

### Event Catalog

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/event-categories/` | None | `EventCategoryViewSet` | List event categories |
| POST | `{{base_url}}/public/event-categories/` | Admin bearer | `EventCategoryViewSet` | Create event category |
| GET | `{{base_url}}/public/event-categories/{{category_id}}/` | None | `EventCategoryViewSet` | Get category detail |
| PUT/PATCH | `{{base_url}}/public/event-categories/{{category_id}}/` | Admin bearer | `EventCategoryViewSet` | Update category |
| DELETE | `{{base_url}}/public/event-categories/{{category_id}}/` | Admin bearer | `EventCategoryViewSet` | Delete category |
| GET | `{{base_url}}/public/events/` | None | `EventViewSet` | List events |
| POST | `{{base_url}}/public/events/` | Admin bearer | `EventViewSet` | Create event |
| GET | `{{base_url}}/public/events/{{event_id}}/` | None | `EventViewSet` | Get event detail |
| PUT/PATCH | `{{base_url}}/public/events/{{event_id}}/` | Admin bearer | `EventViewSet` | Update event |
| DELETE | `{{base_url}}/public/events/{{event_id}}/` | Admin bearer | `EventViewSet` | Delete event |

### Schedules

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/schedules/` | None | `EventScheduleViewSet` | List schedules |
| GET | `{{base_url}}/public/schedules/?event={{event_id}}` | None | `EventScheduleViewSet` | List schedules filtered by event |
| POST | `{{base_url}}/public/schedules/` | Admin bearer | `EventScheduleViewSet` | Create schedule |
| GET | `{{base_url}}/public/schedules/{{schedule_id}}/` | None | `EventScheduleViewSet` | Get schedule detail |
| PUT/PATCH | `{{base_url}}/public/schedules/{{schedule_id}}/` | Admin bearer | `EventScheduleViewSet` | Update schedule |
| DELETE | `{{base_url}}/public/schedules/{{schedule_id}}/` | Admin bearer | `EventScheduleViewSet` | Delete schedule |

### Public Tryout Application Flow

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| POST | `{{base_url}}/public/tryouts/send-otp/` | None | `TryoutSendOtpView` | Validate Turnstile and send school email OTP |
| POST | `{{base_url}}/public/tryouts/verify-otp/` | None | `TryoutVerifyOtpView` | Verify school email OTP |
| POST | `{{base_url}}/public/tryouts/apply/` | None | `TryoutApplyView` | Submit verified public tryout application |

### Tryout Application Review

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/tryout-applications/` | Admin/rep bearer | `TryoutApplicationViewSet` | List verified applications; reps scoped to department |
| POST | `{{base_url}}/public/tryout-applications/` | Admin bearer | `TryoutApplicationViewSet` | Admin create application row |
| GET | `{{base_url}}/public/tryout-applications/{{tryout_application_id}}/` | Admin/rep bearer | `TryoutApplicationViewSet` | Get application detail |
| PUT/PATCH | `{{base_url}}/public/tryout-applications/{{tryout_application_id}}/` | Admin/rep bearer | `TryoutApplicationViewSet` | Review/update application status |
| DELETE | `{{base_url}}/public/tryout-applications/{{tryout_application_id}}/` | Admin/rep bearer | `TryoutApplicationViewSet` | Delete application if permitted |
| POST | `{{base_url}}/public/tryout-applications/{{tryout_application_id}}/convert/` | Admin/rep bearer | `TryoutApplicationViewSet.convert()` | Convert selected applicant to athlete |

### Athletes / Participants

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/athletes/` | Admin/rep bearer | `AthleteViewSet` | List athletes; reps scoped to department |
| POST | `{{base_url}}/public/athletes/` | Admin/rep bearer | `AthleteViewSet` | Create athlete |
| GET | `{{base_url}}/public/athletes/{{athlete_id}}/` | Admin/rep bearer | `AthleteViewSet` | Get athlete detail |
| PUT/PATCH | `{{base_url}}/public/athletes/{{athlete_id}}/` | Admin/rep bearer | `AthleteViewSet` | Update athlete |
| DELETE | `{{base_url}}/public/athletes/{{athlete_id}}/` | Admin/rep bearer | `AthleteViewSet` | Delete athlete |

### Registrations / Rosters

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/registrations/` | Admin/rep bearer | `EventRegistrationViewSet` | List registrations; reps scoped to department |
| POST | `{{base_url}}/public/registrations/` | Admin/rep bearer | `EventRegistrationViewSet` | Submit registration |
| GET | `{{base_url}}/public/registrations/{{registration_id}}/` | Admin/rep bearer | `EventRegistrationViewSet` | Get registration detail |
| PUT/PATCH | `{{base_url}}/public/registrations/{{registration_id}}/` | Admin/rep bearer | `EventRegistrationViewSet` | Update status, notes, or roster IDs |
| DELETE | `{{base_url}}/public/registrations/{{registration_id}}/` | Admin/rep bearer | `EventRegistrationViewSet` | Delete registration |

### Match Results

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/match-results/` | None | `MatchResultViewSet` | List match results |
| POST | `{{base_url}}/public/match-results/` | Admin bearer | `MatchResultViewSet` | Create match result |
| GET | `{{base_url}}/public/match-results/{{match_result_id}}/` | None | `MatchResultViewSet` | Get match result detail |
| PUT/PATCH | `{{base_url}}/public/match-results/{{match_result_id}}/` | Admin bearer | `MatchResultViewSet` | Update match result |
| DELETE | `{{base_url}}/public/match-results/{{match_result_id}}/` | Admin bearer | `MatchResultViewSet` | Delete match result |
| POST | `{{base_url}}/public/match-results/{{match_result_id}}/add-set/` | Admin bearer | `MatchResultViewSet.add_set()` | Add set/period score to match |

### Podium / Rank Results

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/podium-results/` | None | `PodiumResultViewSet` | List podium results |
| POST | `{{base_url}}/public/podium-results/` | Admin bearer | `PodiumResultViewSet` | Create rank-based podium result |
| GET | `{{base_url}}/public/podium-results/{{podium_result_id}}/` | None | `PodiumResultViewSet` | Get podium result detail |
| PUT/PATCH | `{{base_url}}/public/podium-results/{{podium_result_id}}/` | Admin bearer | `PodiumResultViewSet` | Update podium result |
| DELETE | `{{base_url}}/public/podium-results/{{podium_result_id}}/` | Admin bearer | `PodiumResultViewSet` | Delete podium result |

### Medal Ledger and Medal Tally

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/medal-records/` | None | `MedalRecordViewSet` | List medal ledger records |
| GET | `{{base_url}}/public/medal-records/?department={{department_id}}` | None | `MedalRecordViewSet` | List medals for one department |
| POST | `{{base_url}}/public/medal-records/` | Admin bearer | `MedalRecordViewSet` | Create medal record |
| GET | `{{base_url}}/public/medal-records/{{medal_record_id}}/` | None | `MedalRecordViewSet` | Get medal record detail |
| PUT/PATCH | `{{base_url}}/public/medal-records/{{medal_record_id}}/` | Admin bearer | `MedalRecordViewSet` | Update medal record |
| DELETE | `{{base_url}}/public/medal-records/{{medal_record_id}}/` | Admin bearer | `MedalRecordViewSet` | Delete medal record |
| GET | `{{base_url}}/public/medal-tally/` | None | `MedalTallyViewSet` | List standings ordered by gold, silver, bronze, department name |
| GET | `{{base_url}}/public/medal-tally/{{medal_tally_id}}/` | None | `MedalTallyViewSet` | Get one tally row by tally id |

### Public News and Admin News

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| GET | `{{base_url}}/public/news/` | None | `PublicNewsArticleViewSet` | List published news only |
| GET | `{{base_url}}/public/news/?article_type=announcement` | None | `PublicNewsArticleViewSet` | Filter public news by article type |
| GET | `{{base_url}}/public/news/?department={{department_id}}` | None | `PublicNewsArticleViewSet` | Filter public news by department |
| GET | `{{base_url}}/public/news/?event={{event_id}}` | None | `PublicNewsArticleViewSet` | Filter public news by event |
| GET | `{{base_url}}/public/news/?q=finals` | None | `PublicNewsArticleViewSet` | Search public news title |
| GET | `{{base_url}}/public/news/{{news_slug}}/` | None | `PublicNewsArticleViewSet` | Get published article detail by slug |
| GET | `{{base_url}}/admin/news/` | Admin bearer | `AdminNewsArticleViewSet` | List all news, including drafts |
| POST | `{{base_url}}/admin/news/` | Admin bearer | `AdminNewsArticleViewSet` | Create news |
| GET | `{{base_url}}/admin/news/{{news_id}}/` | Admin bearer | `AdminNewsArticleViewSet` | Get admin news detail by id |
| PUT/PATCH | `{{base_url}}/admin/news/{{news_id}}/` | Admin bearer | `AdminNewsArticleViewSet` | Update news |
| DELETE | `{{base_url}}/admin/news/{{news_id}}/` | Admin bearer | `AdminNewsArticleViewSet` | Delete news |

### Rooney and AI Recaps

| Method | URL | Auth | Backend Handler | Purpose |
| --- | --- | --- | --- | --- |
| POST | `{{base_url}}/public/rooney/query/` | None | `RooneyQueryView` | Ask grounded Rooney question |
| GET | `{{base_url}}/public/rooney-logs/` | Admin bearer | `RooneyQueryLogViewSet` | List Rooney query logs |
| GET | `{{base_url}}/public/rooney-logs/{{rooney_log_id}}/` | Admin bearer | `RooneyQueryLogViewSet` | Get Rooney query log detail |
| GET | `{{base_url}}/admin/ai-recaps/` | Admin bearer | `AIRecapViewSet` | List AI recap drafts |
| POST | `{{base_url}}/admin/ai-recaps/` | Admin bearer | `AIRecapViewSet` | Create AI recap draft manually through model serializer |
| GET | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/` | Admin bearer | `AIRecapViewSet` | Get AI recap detail |
| PUT/PATCH | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/` | Admin bearer | `AIRecapViewSet` | Edit recap draft text/status |
| DELETE | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/` | Admin bearer | `AIRecapViewSet` | Delete recap draft |
| POST | `{{base_url}}/admin/ai-recaps/generate/` | Admin bearer | `AIRecapViewSet.generate()` | Generate recap from finalized schedule/result context |
| POST | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/approve/` | Admin bearer | `AIRecapViewSet.approve()` | Mark recap approved |
| POST | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/discard/` | Admin bearer | `AIRecapViewSet.discard()` | Mark recap discarded |
| POST | `{{base_url}}/admin/ai-recaps/{{ai_recap_id}}/publish/` | Admin bearer | `AIRecapViewSet.publish()` | Publish recap as official news |

## Common Request Bodies

### Create Venue

```json
{
  "name": "University Gymnasium",
  "campus": "Lucena Main Campus",
  "building": "Indoor Sports Courts",
  "address": "MSEUF Lucena Main Campus",
  "location": "Indoor sports complex",
  "is_indoor": true,
  "is_active": true,
  "notes": "Primary indoor venue for ball games"
}
```

### Create Venue Area

```json
{
  "venue": {{venue_id}},
  "name": "Indoor Court A",
  "capacity": 300
}
```

### Create Event

```json
{
  "name": "Men's Basketball Finals",
  "slug": "mens-basketball-finals",
  "category": {{category_id}},
  "division": "Men",
  "result_family": "match_based",
  "competition_format": "Single elimination",
  "best_of": 3,
  "team_size_min": 5,
  "team_size_max": 5,
  "roster_size_max": 15,
  "medal_bearing": true,
  "ruleset_ref": "MSEUF Intramurals basketball rules",
  "sort_order": 10,
  "is_program_event": false,
  "status": "scheduled"
}
```

### Create Schedule

```json
{
  "event": {{event_id}},
  "venue": {{venue_id}},
  "venue_area": {{venue_area_id}},
  "phase": "Finals",
  "round_label": "Gold medal match",
  "scheduled_start": "2026-05-01T09:00:00+08:00",
  "scheduled_end": "2026-05-01T11:00:00+08:00",
  "status": "scheduled",
  "notes": "Officials assigned by sports coordinator"
}
```

### Create Athlete

```json
{
  "student_number": "2026-00001",
  "full_name": "Juan Dela Cruz",
  "department": {{department_id}},
  "program_course": "BS Computer Science",
  "year_level": "2nd Year",
  "is_enrolled": true,
  "medical_cleared": true
}
```

### Submit Registration

```json
{
  "schedule": {{schedule_id}},
  "department": {{department_id}},
  "status": "submitted",
  "roster_athlete_ids": [{{athlete_id}}]
}
```

### Public Tryout OTP

```json
{
  "full_name": "Juan Dela Cruz",
  "student_no": "2026-00001",
  "school_email": "juan@student.mseuf.edu.ph",
  "department": {{department_id}},
  "schedule": {{schedule_id}},
  "turnstile_token": "{{turnstile_token}}"
}
```

Real OTP sending requires valid backend `TURNSTILE_SECRET_KEY`, Brevo env values, and a real Turnstile token from the frontend widget.

### Public Tryout Apply

```json
{
  "full_name": "Juan Dela Cruz",
  "student_no": "2026-00001",
  "school_email": "juan@student.mseuf.edu.ph",
  "department": {{department_id}},
  "schedule": {{schedule_id}},
  "program": "BS Computer Science",
  "year_level": "2nd Year",
  "contact_no": "09171234567",
  "prior_experience": "High school varsity",
  "notes": "Available after class hours",
  "consent": true
}
```

### Create Match Result

```json
{
  "schedule": {{schedule_id}},
  "home_department": {{department_id}},
  "away_department": 2,
  "home_score": 78,
  "away_score": 72,
  "winner": {{department_id}},
  "is_draw": false,
  "is_final": true
}
```

### Create Podium Result

```json
{
  "schedule": {{schedule_id}},
  "department": {{department_id}},
  "rank": 1,
  "medal": "gold",
  "performance_value": "58.20",
  "performance_unit": "seconds",
  "is_final": true
}
```

### Create Admin News Article

```json
{
  "title": "Basketball Finals Schedule Released",
  "slug": "basketball-finals-schedule-released",
  "summary": "The official basketball finals schedule has been released.",
  "body_md": "The Sports Coordinator has confirmed the final schedule for basketball.",
  "article_type": "schedule_update",
  "source_label": "Sports Coordinator",
  "event": {{event_id}},
  "department": null,
  "status": "draft",
  "ai_generated": false
}
```

### Ask Rooney

```json
{
  "question": "Who is leading the medal tally right now?"
}
```

### Generate AI Recap

Use either a `match_result_id` or `schedule_id`.

```json
{
  "match_result_id": {{match_result_id}}
}
```

## Suggested Postman Collection Structure

Create folders in this order:

1. `00 Auth`
2. `01 Public Read`
3. `02 Core Admin`
4. `03 Events and Schedules`
5. `04 Tryout Public Flow`
6. `05 Department Workflow`
7. `06 Results and Medal Tally`
8. `07 News`
9. `08 Rooney and AI Recaps`

Recommended smoke-test order:

1. `POST /auth/login/`
2. `GET /auth/me/`
3. `GET /public/departments/`
4. `GET /public/event-categories/`
5. `GET /public/events/`
6. `GET /public/schedules/`
7. `GET /public/medal-tally/`
8. `GET /admin/news/`
9. `GET /admin/ai-recaps/`
10. `POST /auth/logout/`

## Expected Status Codes

| Status | Meaning |
| --- | --- |
| `200` | Successful read/update/action |
| `201` | Created |
| `204` | Deleted |
| `400` | Validation error or business rule failure |
| `401` | Missing/invalid access token or missing/invalid refresh cookie |
| `403` | Authenticated but not allowed |
| `404` | Resource not found |

## Common Testing Problems

### `401 Unauthorized` on Admin Endpoints

Check:

- Login succeeded.
- `access_token` environment variable is set.
- Authorization type is Bearer Token.
- Token value is `{{access_token}}`.
- You logged in as an admin or superuser account.

### Refresh Fails in Postman

Check:

- Login was called first.
- Cookie jar contains `enverga_refresh` for `localhost`.
- Request URL uses the same host as login, such as `localhost` vs `127.0.0.1`.
- Backend `JWT_REFRESH_COOKIE_SECURE=False` for local plain HTTP.

### Tryout OTP Fails

Check:

- Email ends with `@student.mseuf.edu.ph`.
- `turnstile_token` is a real token from the frontend widget.
- Backend has real `TURNSTILE_SECRET_KEY`.
- Backend has Brevo sender/API env values.
- Rate limits have not been exceeded.

### Department Rep Sees Empty Data

Check:

- User has a `UserProfile`.
- Profile role is `department_rep`.
- Profile is linked to a department.
- The test data belongs to that same department.

### Schedule Create/Update Fails

Check:

- `scheduled_end` is later than `scheduled_start`.
- `venue_area` belongs to the selected `venue`.
- The same venue area does not have an overlapping active schedule.

## Security Testing Notes

For demo-safe negative tests:

- Call `/api/admin/news/` without a bearer token; expect `401`.
- Login as a department representative and call `/api/admin/news/`; expect `403`.
- Login as one department representative and verify `/api/public/athletes/` only returns that department's athletes.
- Try creating a registration with an athlete from another department; expect validation failure.
- Call `/api/auth/logout/`, clear `access_token`, then call `/api/auth/me/`; expect `401`.
