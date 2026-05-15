# Full local stack: sync student UI -> frontend2/, Postgres, API + UI on :8000
$ErrorActionPreference = "Stop"
$BackendDir = Split-Path -Parent $PSScriptRoot
Set-Location $BackendDir

Write-Host "Syncing student HTML into ../frontend2/ ..."
& "$PSScriptRoot\sync-frontend2.ps1"

if (-not (Test-Path "..\\frontend2\\index.html")) {
    throw "frontend2/index.html missing after sync."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env - set POSTGRES_PASSWORD and GROQ_API_KEY."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "Starting PostgreSQL (Docker)..."
docker compose up -d

Write-Host "Running migrations..."
.\.venv\Scripts\python.exe manage.py migrate

Write-Host ""
Write-Host "============================================"
Write-Host "  UI:      http://localhost:8000/"
Write-Host "  Create:  http://localhost:8000/create-ad.html"
Write-Host "  Sign in: http://localhost:8000/signin.html"
Write-Host "  API:     http://localhost:8000/api/"
Write-Host "  Docs:    http://localhost:8000/docs/"
Write-Host "============================================"
Write-Host ""

.\.venv\Scripts\python.exe manage.py runserver 8000
