# Backend setup

## Requirements

- Python 3.11+
- PostgreSQL 14+ (or Docker)

## Steps

```powershell
cd backend
copy .env.example .env
# Edit .env — set POSTGRES_* and GROQ_API_KEY

python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

docker compose up -d
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 8000
```

- API: http://localhost:8000/api/
- Swagger: http://localhost:8000/docs/
- Admin: http://localhost:8000/admin/

## Environment variables

See `.env.example` in the `backend` folder.

`GROQ_API_KEY` is required for `POST /api/ad-briefs/{id}/generate/`. Without it, the API returns **503** (no fake ads).
