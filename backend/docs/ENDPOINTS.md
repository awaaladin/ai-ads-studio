# API Endpoints

Base: `http://localhost:8000`

Auth header (protected routes): `Authorization: Bearer <access_token>`

---

## Auth — `/api/auth/`

| Method | Path |
|--------|------|
| POST | `/api/auth/register/` |
| POST | `/api/auth/login/` |
| POST | `/api/auth/refresh/` |
| POST | `/api/auth/logout/` |
| GET | `/api/auth/me/` |

---

## Studio — `/api/`

| Method | Path |
|--------|------|
| GET | `/api/` |
| GET | `/api/dashboard/` |
| GET | `/api/analytics/` |
| GET | `/api/ad-briefs/` |
| POST | `/api/ad-briefs/` |
| GET | `/api/ad-briefs/<brief_id>/` |
| POST | `/api/ad-briefs/<brief_id>/generate/` |
| GET | `/api/ad-briefs/<brief_id>/variants/` |
| GET | `/api/campaigns/` |
| POST | `/api/campaigns/` |
| GET | `/api/campaigns/<campaign_id>/` |
| PUT | `/api/campaigns/<campaign_id>/` |
| PATCH | `/api/campaigns/<campaign_id>/` |
| DELETE | `/api/campaigns/<campaign_id>/` |
| GET | `/api/notifications/` |
| PATCH | `/api/notifications/<notification_id>/read/` |
| GET | `/api/projects/` |
| POST | `/api/projects/` |
| GET | `/api/projects/<project_id>/` |
| POST | `/api/projects/<project_id>/generate/` |
| GET | `/api/projects/<project_id>/creatives/` |

---

## Docs

| Method | Path |
|--------|------|
| GET | `/api/schema/` |
| GET | `/docs/` |

---

## Local UI (DEBUG)

| Method | Path |
|--------|------|
| GET | `/config.js` |
| GET | `/` |
| GET | `/*.html`, `/*.js`, `/*.css` |

---

## Ad generation

`POST /api/ad-briefs/<brief_id>/generate/` uses Groq if `GROQ_API_KEY` in `.env` is valid; otherwise returns template variants (no AI required).
