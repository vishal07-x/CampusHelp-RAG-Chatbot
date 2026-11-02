@echo off
echo ==========================================
echo   Starting CampusHelp RAG Backend Server  
echo ==========================================

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
)

echo Seeding institutional sample documents...
venv\Scripts\python seed_sample_docs.py

echo Starting FastAPI application at http://localhost:8000 (Swagger docs at /docs)...
venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
