from fastapi import APIRouter
from app.api.v1.endpoints import (
    projects,
    applications,
    test_runs,
    test_cases,
    test_suites,
    bugs,
    reports,
    settings as settings_api,
    playground,
)

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
api_router.include_router(test_runs.router, prefix="/test-runs", tags=["test-runs"])
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["test-cases"])
api_router.include_router(test_suites.router, prefix="/test-suites", tags=["test-suites"])
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(settings_api.router, prefix="/settings", tags=["settings"])
api_router.include_router(playground.router, prefix="/playground", tags=["playground"])
