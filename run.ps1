$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$Python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Host "ERROR: No se encontró el entorno virtual .venv" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===================================="
Write-Host " THE INTELLIGENCE SYSTEM"
Write-Host "===================================="
Write-Host ""
Write-Host "Iniciando API FastAPI..."
Write-Host "Documentacion: http://127.0.0.1:8000/docs"
Write-Host ""

& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
