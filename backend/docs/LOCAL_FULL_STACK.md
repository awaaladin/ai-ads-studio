# Run backend + student frontend together (one port)

The real UI is **HTML + Tailwind** in `frontend2/` (built by students on branches like `ad-page`, `AuthPage`, etc.).  
The old **`frontend/`** Next.js app is **not used** — remove it if it appears on your branch.

## One command

```powershell
cd backend
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1
```

This will:

1. **Sync** all student `frontend2/` files from GitHub branches into `../frontend2/`
2. Start **PostgreSQL** (Docker)
3. Run **migrations**
4. Start Django on **http://localhost:8000**

## URLs

| URL | Page |
|-----|------|
| http://localhost:8000/ | Dashboard |
| http://localhost:8000/create-ad.html | Create Ad |
| http://localhost:8000/signin.html | Sign in |
| http://localhost:8000/signup.html | Sign up |
| http://localhost:8000/Dashboard.html | Dashboard (Dashboard branch) |
| http://localhost:8000/settings.html | Settings |
| http://localhost:8000/notification.html | Notifications |
| http://localhost:8000/api/ | REST API |
| http://localhost:8000/docs/ | Swagger |

## Refresh UI from students

```powershell
powershell -File backend/scripts/sync-frontend2.ps1
```

## Push backend only

```powershell
git checkout backend
git add backend/
git commit -m "your API change"
git push origin backend
```

Do **not** commit `frontend2/` when you only intend to ship API changes (students own those branches).
