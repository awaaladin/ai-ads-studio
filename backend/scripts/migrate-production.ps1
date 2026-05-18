# Apply Django migrations to your production Supabase database.
# Usage (PowerShell):
#   $env:DATABASE_URL = "postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres?sslmode=require"
#   $env:DJANGO_SECRET_KEY = "same-as-vercel"
#   .\scripts\migrate-production.ps1

$ErrorActionPreference = "Stop"
$BackendDir = Split-Path -Parent $PSScriptRoot
Set-Location $BackendDir

if (-not $env:DATABASE_URL) {
    Write-Host "ERROR: Set DATABASE_URL to your Supabase connection string first." -ForegroundColor Red
    Write-Host '  $env:DATABASE_URL = "postgresql://postgres:...@db.xxx.supabase.co:5432/postgres?sslmode=require"'
    exit 1
}

if (-not $env:DJANGO_SECRET_KEY) {
    Write-Host "WARNING: DJANGO_SECRET_KEY not set — using temporary value for migrate only." -ForegroundColor Yellow
    $env:DJANGO_SECRET_KEY = "migrate-only-temp-secret"
}

$env:DJANGO_DEBUG = "false"
Remove-Item Env:USE_SQLITE -ErrorAction SilentlyContinue

Write-Host "Running migrations against production database..." -ForegroundColor Cyan
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Done. Redeploy Vercel, then check:" -ForegroundColor Green
Write-Host "  GET https://ai-ads-studio-kappa.vercel.app/api/"
Write-Host '  Expect: "database": "connected", "migrations": "applied"'
