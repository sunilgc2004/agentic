@echo off
echo ========================================================
echo        Starting AI QA Testing Agent (STAGING MODE)
echo ========================================================
echo.
echo Mode: STAGING
echo Environment: staging
echo Database: backend/data/qa_agent_staging.db
echo.

set ENVIRONMENT=staging
set DATABASE_URL=sqlite:///./data/qa_agent_staging.db

echo [1/2] Launching Staging Backend (FastAPI on http://127.0.0.1:8000)...
start "AI QA Agent [STAGING] - Backend" cmd /k "cd backend && set ENVIRONMENT=staging && set DATABASE_URL=sqlite:///./data/qa_agent_staging.db && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/2] Launching Staging Frontend (React on http://localhost:5173)...
start "AI QA Agent [STAGING] - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 3 >nul

echo Opening Staging Dashboard in your browser...
start http://localhost:5173

echo.
echo ========================================================
echo Staging environment is now running:
echo   - Staging Dashboard: http://localhost:5173
echo   - Staging Backend API: http://127.0.0.1:8000/docs
echo ========================================================
