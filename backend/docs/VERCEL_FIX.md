# Vercel not updating? Fix register 500

## Symptom

- `GET /api/` returns only `{"message": "AI Ads Studio API is running"}` (old code)
- `POST /api/auth/register/` returns **500**
- `/static/rest_framework/...` returns **404**

## Cause

1. Vercel is **not deploying** the `backend` branch (wrong root directory or branch).
2. **Migrations** never ran on Supabase (`accounts_userprofile` table missing).

## Fix in Vercel Dashboard

1. **Settings → General → Root Directory**  
   - If your repo root is `ai-ads-studio-1`: leave **empty** (use root `vercel.json`)  
   - OR set to **`backend`** (uses `backend/vercel.json`)

2. **Settings → Git → Production Branch** → **`backend`**

3. **Settings → Environment Variables** (Production):
   - `DATABASE_URL` = Supabase URL with `?sslmode=require`
   - `DJANGO_SECRET_KEY` = long random string
   - `DJANGO_DEBUG` = `false`
   - `DJANGO_ALLOWED_HOSTS` = `ai-ads-studio-kappa.vercel.app,.vercel.app`
   - `EXPOSE_API_ERRORS` = `true` (temporary, to see real errors)
   - Do **not** set `USE_SQLITE`

4. **Deployments → Redeploy** latest commit (must include `version` in `/api/` response).

## Verify deploy

```http
GET https://ai-ads-studio-kappa.vercel.app/api/
```

**New code** returns:

```json
{
  "status": "ok",
  "message": "AI Ads Studio API is running",
  "version": "abc123...",
  "database": "connected",
  "migrations": "applied"
}
```

## Test register

```json
POST /api/auth/register/
{
  "email": "student@test.com",
  "password": "TestPass123!",
  "password_confirm": "TestPass123!",
  "full_name": "Test Student"
}
```

Expect **201 Created**, not 500.
