@echo off
title Autonomous AI QA Testing Agent
echo ========================================================
echo        Starting Autonomous AI QA Testing Agent
echo ========================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)...
start "AI QA Agent - Backend" /D "%SCRIPT_DIR%backend" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Launching Frontend Server (React on http://localhost:5173)...
start "AI QA Agent - Frontend" /D "%SCRIPT_DIR%frontend" cmd /k "npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 5 >nul

echo Opening AI QA Agent Dashboard in your browser...
start http://localhost:5173

echo.
echo ========================================================
echo Platform is now running locally:
echo   - Web UI: http://localhost:5173
echo   - Backend API Docs: http://127.0.0.1:8000/docs
echo ========================================================
