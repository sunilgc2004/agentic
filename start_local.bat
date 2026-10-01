@echo off
echo ========================================================
echo        Starting Autonomous AI QA Testing Agent
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching Backend Server (FastAPI on http://127.0.0.1:8000)...
start "AI QA Agent - Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Launching Frontend Server (React + Vite on http://localhost:5173)...
start "AI QA Agent - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

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
