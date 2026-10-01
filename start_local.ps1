# PowerShell One-Click Local Launcher for Autonomous AI QA Testing Agent
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Starting Autonomous AI QA Testing Agent" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Launching Backend Server on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot\backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

Write-Host "[2/2] Launching Frontend Server on http://localhost:5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$projectRoot\frontend'; npm run dev"

Write-Host "Waiting for servers to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 4

Write-Host "Opening AI QA Agent Dashboard in your browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Platform is now running locally:" -ForegroundColor Green
Write-Host "  - Web UI: http://localhost:5173" -ForegroundColor White
Write-Host "  - Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
