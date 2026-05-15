# Sync student HTML/Tailwind UI into repo frontend2/ from remote branches.
# Run from repo root or backend/:  powershell -File backend/scripts/sync-frontend2.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$BackendDir = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $BackendDir
$Dest = Join-Path $RepoRoot "frontend2"

Set-Location $RepoRoot
Write-Host "Fetching branches..."
git fetch --all

if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest | Out-Null }

$branches = @(
    "ad-page",
    "AuthPage",
    "Dashboard",
    "Analytics",
    "open-source",
    "notification",
    "campaigns",
    "Gldev"
)

foreach ($branch in $branches) {
    Write-Host "Merging frontend2 from origin/$branch ..."
    $files = git ls-tree -r --name-only "origin/$branch" 2>$null | Where-Object { $_ -like "frontend2/*" }
    if (-not $files) { continue }
    foreach ($file in $files) {
        $relative = $file -replace "^frontend2/", ""
        $outPath = Join-Path $Dest $relative
        $outDir = Split-Path $outPath -Parent
        if ($outDir -and -not (Test-Path $outDir)) {
            New-Item -ItemType Directory -Path $outDir -Force | Out-Null
        }
        git show "origin/${branch}:$file" | Set-Content -Path $outPath -Encoding UTF8
    }
}

# Local helpers (not from student branches)
Copy-Item (Join-Path $ScriptDir "..\frontend2-nav.js") (Join-Path $Dest "nav.js") -Force
Copy-Item (Join-Path $ScriptDir "..\frontend2-auth.js") (Join-Path $Dest "auth.js") -Force
Copy-Item (Join-Path $ScriptDir "..\frontend2-app.js") (Join-Path $Dest "app.js") -Force

$headTags = @(
    '<script src="/config.js"></script>',
    '<script src="/auth.js"></script>'
)
$bodyExtra = '<script src="/app.js"></script>'
$bodyTag = '<script src="/nav.js"></script>'

Get-ChildItem $Dest -Filter "*.html" -Recurse | ForEach-Object {
    $html = Get-Content $_.FullName -Raw
    foreach ($tag in $headTags) {
        if ($html -notmatch [regex]::Escape($tag)) {
            $html = $html -replace "</head>", "  $tag`n</head>"
        }
    }
    if ($html -notmatch [regex]::Escape($bodyTag)) {
        $html = $html -replace "</body>", "  $bodyTag`n</body>"
    }
    if ($html -notmatch [regex]::Escape($bodyExtra) -and $html -match "app-main|create-ad|notification|settings") {
        $html = $html -replace "</body>", "  $bodyExtra`n</body>"
    }
    Set-Content -Path $_.FullName -Value $html -Encoding UTF8
}

Write-Host ""
Write-Host "Synced to: $Dest"
Get-ChildItem $Dest -File | ForEach-Object { Write-Host "  - $($_.Name)" }
