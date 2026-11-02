Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Starting CampusHelp Frontend Client     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Set-Location -Path "$PSScriptRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting Vite development server at http://localhost:5173..." -ForegroundColor Green
npm run dev
