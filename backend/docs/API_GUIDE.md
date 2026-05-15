# AI Ads Studio — Backend API Guide (for teaching `fetch`)

**Base URL (local):** `http://localhost:8000/api`  
**Interactive docs:** http://localhost:8000/docs/  
**OpenAPI JSON:** http://localhost:8000/api/schema/

The frontend (`frontend2/`) is **HTML + Tailwind + JavaScript**. It does not call the API yet. This document maps each UI screen to the REST endpoints students should wire with `fetch`.

---

## 1. Quick start

```javascript
const API_BASE = "http://localhost:8000/api";

function getToken() {
  return localStorage.getItem("access_token");
}

function authHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}
```

After login, save tokens:

```javascript
localStorage.setItem("access_token", data.access);
localStorage.setItem("refresh_token", data.refresh);
```

---

## 2. Authentication (`signin.html` / `signup.html`)

### Register — `POST /api/auth/register/`

**HTML fields (signup):** Full name, Work email, Password

```javascript
const res = await fetch(`${API_BASE}/auth/register/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "student@school.edu",
    work_email: "student@school.edu",
    full_name: "Jane Doe",
    password: "securepass123",
    password_confirm: "securepass123",
  }),
});
const user = await res.json();
```

**201 response:**

```json
{
  "id": 1,
  "username": "student",
  "email": "student@school.edu",
  "first_name": "Jane",
  "last_name": "Doe"
}
```

### Login — `POST /api/auth/login/`

**HTML fields (signin):** Email, Password

```javascript
const res = await fetch(`${API_BASE}/auth/login/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "student@school.edu",
    password: "securepass123",
  }),
});
const data = await res.json();
```

**200 response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Current user — `GET /api/auth/me/` (requires token)

```javascript
const res = await fetch(`${API_BASE}/auth/me/`, {
  headers: authHeaders(),
});
```

### Logout — `POST /api/auth/logout/`

```javascript
await fetch(`${API_BASE}/auth/logout/`, {
  method: "POST",
  headers: authHeaders(),
  body: JSON.stringify({ refresh: localStorage.getItem("refresh_token") }),
});
localStorage.removeItem("access_token");
localStorage.removeItem("refresh_token");
```

### Refresh token — `POST /api/auth/refresh/`

```javascript
const res = await fetch(`${API_BASE}/auth/refresh/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ refresh: localStorage.getItem("refresh_token") }),
});
const data = await res.json();
localStorage.setItem("access_token", data.access);
```

---

## 3. Dashboard (`index.html`)

### Summary — `GET /api/dashboard/`

No auth required (shows public briefs). Logged-in users see their campaigns too.

```javascript
const res = await fetch(`${API_BASE}/dashboard/`, {
  headers: authHeaders(),
});
const dashboard = await res.json();
```

**200 response:**

```json
{
  "total_campaigns": 2,
  "active_campaigns": 1,
  "total_briefs": 5,
  "total_variants": 12,
  "analytics": {
    "impressions": 1000,
    "clicks": 50,
    "ctr": 5.0,
    "spend": "120.00"
  },
  "recent_campaigns": [],
  "recent_briefs": [],
  "unread_notifications": []
}
```

Use `dashboard.recent_briefs` to populate the dashboard list.  
Use `dashboard.analytics` for Analytics nav stats.

---

## 4. Create Ad (`create-ad.html`)

### Form field mapping

| HTML `name` / `id` | JSON field |
|--------------------|------------|
| `prod-service` | `product_service` |
| `audience` | `audience` |
| `tone` | `tone` |
| `platform` | `platform` |
| `key-message` | `key_message` |

### Step 1 — Save brief — `POST /api/ad-briefs/`

```javascript
const form = document.querySelector("form");

const res = await fetch(`${API_BASE}/ad-briefs/`, {
  method: "POST",
  headers: authHeaders(),
  body: JSON.stringify({
    product_service: form["prod-service"].value,
    audience: form.audience.value,
    tone: form.tone.value,
    platform: form.platform.value,
    key_message: form["key-message"].value,
  }),
});

if (!res.ok) {
  const err = await res.json();
  alert(err.detail || "Failed to save brief");
  throw new Error(res.status);
}

const brief = await res.json();
```

**201 response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "product_service": "Lightweight running sneakers",
  "audience": "Urban commuters 25-40",
  "tone": "friendly",
  "platform": "meta",
  "key_message": "Free shipping this week",
  "created_at": "2026-05-15T12:00:00Z",
  "updated_at": "2026-05-15T12:00:00Z"
}
```

### Step 2 — Generate variants — `POST /api/ad-briefs/{id}/generate/`

Call when the user clicks **Generate ads** (requires `GROQ_API_KEY` on the server).

```javascript
const res = await fetch(`${API_BASE}/ad-briefs/${brief.id}/generate/`, {
  method: "POST",
  headers: authHeaders(),
});

const variants = await res.json();
```

**201 response (array):**

```json
[
  {
    "id": "...",
    "brief_id": "...",
    "headline": "Run lighter. Feel stronger.",
    "body": "Our sneakers are built for city miles...",
    "cta": "Shop now",
    "platform": "meta",
    "created_at": "..."
  }
]
```

Render each variant in the **Generated variants** panel.

### Step 3 — Load saved variants — `GET /api/ad-briefs/{id}/variants/`

```javascript
const res = await fetch(`${API_BASE}/ad-briefs/${briefId}/variants/`, {
  headers: authHeaders(),
});
const variants = await res.json();
```

### List all briefs — `GET /api/ad-briefs/`

```javascript
const res = await fetch(`${API_BASE}/ad-briefs/`, { headers: authHeaders() });
const briefs = await res.json();
```

---

## 5. Campaigns (Campaigns nav + search box)

Requires login.

### List / search — `GET /api/campaigns/?search=summer`

```javascript
const q = encodeURIComponent("summer");
const res = await fetch(`${API_BASE}/campaigns/?search=${q}`, {
  headers: authHeaders(),
});
const campaigns = await res.json();
```

### Create — `POST /api/campaigns/`

```javascript
const res = await fetch(`${API_BASE}/campaigns/`, {
  method: "POST",
  headers: authHeaders(),
  body: JSON.stringify({
    name: "Summer Sneaker Push",
    platform: "meta",
    status: "draft",
    brief_id: brief.id,
  }),
});
```

### Update — `PATCH /api/campaigns/{id}/`

```javascript
await fetch(`${API_BASE}/campaigns/${campaignId}/`, {
  method: "PATCH",
  headers: authHeaders(),
  body: JSON.stringify({ status: "active", impressions: 500, clicks: 25 }),
});
```

### Delete — `DELETE /api/campaigns/{id}/`

```javascript
await fetch(`${API_BASE}/campaigns/${campaignId}/`, {
  method: "DELETE",
  headers: authHeaders(),
});
```

---

## 6. Analytics (`Analytics` nav)

Requires login.

### `GET /api/analytics/`

```javascript
const res = await fetch(`${API_BASE}/analytics/`, { headers: authHeaders() });
const analytics = await res.json();
```

**200 response:**

```json
{
  "impressions": 5000,
  "clicks": 250,
  "ctr": 5.0,
  "spend": "450.00",
  "campaigns": []
}
```

---

## 7. Notifications (`Notifications` nav)

Requires login.

### List — `GET /api/notifications/?unread=true`

```javascript
const res = await fetch(`${API_BASE}/notifications/?unread=true`, {
  headers: authHeaders(),
});
const notifications = await res.json();
```

### Mark read — `PATCH /api/notifications/{id}/read/`

```javascript
await fetch(`${API_BASE}/notifications/${id}/read/`, {
  method: "PATCH",
  headers: authHeaders(),
});
```

---

## 8. Error handling pattern

```javascript
async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...options.headers },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data.detail || JSON.stringify(data);
    throw new Error(`${res.status}: ${msg}`);
  }
  return data;
}
```

| Status | Meaning |
|--------|---------|
| 400 | Validation error (bad JSON or missing fields) |
| 401 | Missing or expired token |
| 403 | Not allowed |
| 404 | Resource not found |
| 503 | AI generation failed (check `GROQ_API_KEY`) |
| 500 | Server error |

---

## 9. CORS

The backend allows all origins when `DJANGO_DEBUG=true`.  
For production, set `CORS_ALLOWED_ORIGINS` in `.env` to your static site URL (e.g. `http://127.0.0.1:5500`).

---

## 10. Full endpoint list

| Method | Path | Auth | Used by page |
|--------|------|------|--------------|
| GET | `/api/` | No | Health check |
| POST | `/api/auth/register/` | No | signup |
| POST | `/api/auth/login/` | No | signin |
| POST | `/api/auth/refresh/` | No | token refresh |
| POST | `/api/auth/logout/` | Yes | sign out |
| GET | `/api/auth/me/` | Yes | profile |
| GET | `/api/dashboard/` | Optional | index (Dashboard) |
| GET/POST | `/api/ad-briefs/` | Optional | create-ad |
| GET | `/api/ad-briefs/{id}/` | Optional | create-ad |
| POST | `/api/ad-briefs/{id}/generate/` | Optional | create-ad |
| GET | `/api/ad-briefs/{id}/variants/` | Optional | create-ad |
| GET/POST | `/api/campaigns/` | Yes | Campaigns |
| GET/PATCH/DELETE | `/api/campaigns/{id}/` | Yes | Campaigns |
| GET | `/api/analytics/` | Yes | Analytics |
| GET | `/api/notifications/` | Yes | Notifications |
| PATCH | `/api/notifications/{id}/read/` | Yes | Notifications |
