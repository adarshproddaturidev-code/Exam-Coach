# ─── start.ps1 ─── Personalized Entrance Exam Coach Launcher ───────────────
Write-Host "🎯 Starting Personalized Entrance Exam Coach..." -ForegroundColor Cyan

$BackendDir = Join-Path $PSScriptRoot "backend"
$VenvDir    = Join-Path $BackendDir "venv"
$EnvFile    = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $BackendDir ".env.example"

# 1. Create virtual environment if not present
if (-not (Test-Path $VenvDir)) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

# 2. Activate & install
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
& $PipExe install -r (Join-Path $BackendDir "requirements.txt") -q

# 3. Copy .env if needed
if (-not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host "⚙️  Created .env from .env.example — edit backend\.env to add your API key." -ForegroundColor Magenta
}

# 4. Start server
$UvicornExe = Join-Path $VenvDir "Scripts\uvicorn.exe"
Write-Host ""
Write-Host "✅ All set! Starting server..." -ForegroundColor Green
Write-Host "   App:     http://localhost:8000" -ForegroundColor White
Write-Host "   API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Set-Location $BackendDir
& $UvicornExe main:app --reload --port 8000
