# AI Ads Studio — Live API Reference

| | |
|---|---|
| **Base URL** | `https://ai-ads-studio-kappa.vercel.app/api` |
| **Interactive docs** | `https://ai-ads-studio-kappa.vercel.app/docs/` |
| **OpenAPI schema** | `https://ai-ads-studio-kappa.vercel.app/api/schema/` |

**Authenticated requests**

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

Tokens from `POST /api/auth/login/` · Refresh via `POST /api/auth/refresh/`

---

## System

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/docs/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/schema/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/legal/terms/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/legal/privacy/` | No |

Health check returns `status`, `database`, and `ai` (`configured` or `fallback_templates`).

---

## Authentication

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/register/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/login/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/refresh/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/logout/` | Yes |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/auth/me/` | Yes |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/password-reset/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/password-reset/confirm/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/auth/verify-email/` | No |

`GET /api/auth/me/` includes `plan`, `generations_this_month`, and `generation_limit`. Set `REQUIRE_EMAIL_VERIFICATION=true` in production when SMTP is configured.

---

## Dashboard

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/dashboard/` | Yes |

---

## Analytics

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/analytics/` | Yes |

---

## Projects

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/projects/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/projects/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/projects/{project_id}/` | No |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/projects/{project_id}/generate/` | No |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/projects/{project_id}/creatives/` | No |

`{project_id}` — UUID

---

## Ad briefs & generation

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/ad-briefs/` | Yes |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/ad-briefs/` | Yes |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/ad-briefs/{brief_id}/` | Yes |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/ad-briefs/{brief_id}/generate/` | Yes |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/ad-briefs/{brief_id}/variants/` | Yes |

`{brief_id}` — UUID

---

## Campaigns

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/` | Yes |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/` | Yes |
| GET | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/{campaign_id}/` | Yes |
| PUT | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/{campaign_id}/` | Yes |
| PATCH | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/{campaign_id}/` | Yes |
| DELETE | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/{campaign_id}/` | Yes |
| POST | `https://ai-ads-studio-kappa.vercel.app/api/campaigns/{campaign_id}/simulate/` | Yes |

`{campaign_id}` — UUID · `GET /api/campaigns/?search=` — optional name filter

**Simulate** bumps impressions/clicks/spend (demo charts). Analytics page auto-refreshes every 8s when logged in.

---

## Notifications

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `https://ai-ads-studio-kappa.vercel.app/api/notifications/` | Yes |
| PATCH | `https://ai-ads-studio-kappa.vercel.app/api/notifications/{notification_id}/read/` | Yes |

`{notification_id}` — UUID · `GET /api/notifications/?unread=true` — unread only

---

## Frontend configuration

```javascript
window.API_BASE = "https://ai-ads-studio-kappa.vercel.app/api";
```

---

## Typical flow

1. `POST /api/auth/register/` or `POST /api/auth/login/`
2. `GET /api/auth/me/`
3. `GET /api/dashboard/`
4. `POST /api/ad-briefs/` → `POST /api/ad-briefs/{brief_id}/generate/`
5. `GET /api/campaigns/` · `GET /api/analytics/` · `GET /api/notifications/`

Detailed request/response bodies: [API_GUIDE.md](./API_GUIDE.md)
