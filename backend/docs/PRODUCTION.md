# Production deployment guide

AI Ads Studio backend is deployable on **Vercel** (current instructor setup), **Render**, or **Railway**. Use Postgres (Supabase recommended) and set env vars before going live.

## Required environment variables

| Variable | Example | Notes |
|----------|---------|--------|
| `DJANGO_SECRET_KEY` | long random string | Never commit |
| `DJANGO_DEBUG` | `false` | Must be false in production |
| `DJANGO_ALLOWED_HOSTS` | `your-app.vercel.app,.vercel.app` | Comma-separated |
| `DATABASE_URL` | `postgresql://...` | Supabase connection string |
| `GROQ_API_KEY` | `gsk_...` | Optional; templates used if missing |
| `SERVE_FRONTEND` | `false` | API-only on Vercel |
| `CORS_ALLOW_ALL` | `true` | For student frontends on any origin |

## Recommended production settings

| Variable | Default | Purpose |
|----------|---------|---------|
| `REQUIRE_EMAIL_VERIFICATION` | `false` | Set `true` when SMTP is configured |
| `GENERATION_LIMIT_FREE` | `25` | Monthly AI generations (free plan) |
| `GENERATION_LIMIT_PRO` | `500` | Pro plan limit |
| `PUBLIC_APP_URL` | your site URL | Links in verification emails |
| `EMAIL_BACKEND` | console in dev | Use SMTP backend in prod |
| `DEFAULT_FROM_EMAIL` | `noreply@...` | Sender for auth emails |
| `THROTTLE_ANON` | `60/minute` | Anonymous API rate limit |
| `THROTTLE_USER` | `120/minute` | Authenticated rate limit |
| `THROTTLE_AUTH` | `10/minute` | Login/register burst limit |
| `THROTTLE_GENERATE` | `30/hour` | AI generation endpoints |
| `SECURE_SSL_REDIRECT` | `true` | Set `false` only if your host handles HTTPS |

## Deploy steps (Vercel)

1. Connect repo; set root directory to `backend`.
2. Add env vars from [VERCEL_ENV_VARS.md](./VERCEL_ENV_VARS.md).
3. Deploy; run migrations against Supabase once:

   ```bash
   cd backend
   python manage.py migrate
   ```

4. **If Vercel build did not migrate Supabase**, run once from your PC:

   ```powershell
   cd backend
   $env:DATABASE_URL = "postgresql://..."   # same as Vercel
   $env:DJANGO_SECRET_KEY = "same-as-vercel"
   .\scripts\migrate-production.ps1
   ```

5. Redeploy after pushing (needs **WhiteNoise** for `/static/rest_framework/` on `/docs/`).

6. Smoke test: `GET /api/` should return:

   ```json
   { "status": "ok", "database": "connected", "migrations": "applied" }
   ```

   If `"migrations": "pending"`, run step 4 again.

## Security checklist

- [ ] Rotate any keys pasted in chat or commits
- [ ] `DJANGO_DEBUG=false`
- [ ] Strong `DJANGO_SECRET_KEY`
- [ ] Postgres RLS / network rules on Supabase
- [ ] Enable `REQUIRE_EMAIL_VERIFICATION` when email works
- [ ] Review `THROTTLE_*` for your class size

## CI

GitHub Actions runs `manage.py check` and `manage.py test` on changes under `backend/`.

## Not included (commercial roadmap)

- Real Meta / Google Ads API integrations
- Billing (Stripe) and plan enforcement beyond quotas
- WAF / DDoS beyond DRF throttling
- SOC2 / formal compliance audits
