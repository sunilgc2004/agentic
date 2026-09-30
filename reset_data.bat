@echo off
echo ========================================================
echo       Autonomous AI QA Agent - Data Reset Tool
echo ========================================================
echo.
echo WARNING: This will delete all Test Runs, Bugs, Screenshots, 
echo and Reports, resetting the application to a clean state.
echo.
set /p confirm="Are you sure you want to proceed? (Y/N): "
if /i "%confirm%" neq "Y" (
    echo Reset cancelled.
    exit /b
)

echo Stopping any running backend processes...
taskkill /F /IM python.exe 2>nul

echo Deleting database...
if exist backend\data\qa_agent.db del /F /Q backend\data\qa_agent.db
if exist backend\data\qa_agent.db-shm del /F /Q backend\data\qa_agent.db-shm
if exist backend\data\qa_agent.db-wal del /F /Q backend\data\qa_agent.db-wal

echo Cleaning evidence screenshots...
for /d %%D in (backend\data\evidence\*) do rd /s /q "%%D"
for %%F in (backend\data\evidence\*) do if not "%%~nxF"==".gitkeep" del /F /Q "%%F"

echo Cleaning generated reports...
for /d %%D in (backend\data\reports\*) do rd /s /q "%%D"
for %%F in (backend\data\reports\*) do if not "%%~nxF"==".gitkeep" del /F /Q "%%F"

echo Initializing fresh database...
cd backend
python -c "from app.database.base import Base; from app.database.session import engine; Base.metadata.create_all(bind=engine); from app.main import seed_initial_data; seed_initial_data(); print('Fresh database created!')"
cd ..

echo.
echo ========================================================
echo SUCCESS: All application data has been completely wiped!
echo ========================================================
pause
