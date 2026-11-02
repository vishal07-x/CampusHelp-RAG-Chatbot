@echo off
echo ==========================================
echo   Starting CampusHelp Frontend Client     
echo ==========================================

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)

echo Starting Vite development server at http://localhost:5173...
call npm run dev
pause
