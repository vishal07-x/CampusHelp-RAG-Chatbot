Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting CampusHelp RAG Backend Server  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\backend"

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\venv\Scripts\pip install -r requirements.txt
}

Write-Host "Seeding institutional sample documents..." -ForegroundColor Yellow
.\venv\Scripts\python seed_sample_docs.py

Write-Host "Starting FastAPI application at http://localhost:8000 (Docs at /docs)..." -ForegroundColor Green
.\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
