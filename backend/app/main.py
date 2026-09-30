from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.api.v1.api import api_router
from app.api.websockets.live_execution import router as ws_router
from app.models.entities import Project, Application, Environment

# Initialize database schema
Base.metadata.create_all(bind=engine)


def seed_initial_data():
    """Seeds a default project and playground application for seamless day-one testing."""
    db = SessionLocal()
    try:
        existing_proj = db.query(Project).filter(Project.name == "Enterprise QA Workspace").first()
        if not existing_proj:
            proj = Project(
                name="Enterprise QA Workspace",
                description="Default workspace containing mission-critical legaltech and arbitration applications."
            )
            db.add(proj)
            db.commit()
            db.refresh(proj)

            app = Application(
                project_id=proj.id,
                name="Arbitration Portal (Playground)",
                base_url="http://localhost:8000/api/v1/playground",
                description="Live enterprise case management sandbox featuring auth, forms, tables, and testable workflows.",
                default_environment="qa",
                auth_type="credentials",
                auth_credentials={"username": "test@example.com", "password": "SecurePass123!"}
            )
            db.add(app)
            db.commit()
            db.refresh(app)

            env = Environment(
                application_id=app.id,
                name="qa",
                url="http://localhost:8000/api/v1/playground",
                is_safe_mode=False
            )
            db.add(env)
            db.commit()
    finally:
        db.close()


seed_initial_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local QA dev & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API and WebSockets
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

# Mount Evidence directory for screenshots preview
app.mount("/evidence", StaticFiles(directory=str(settings.EVIDENCE_DIR)), name="evidence")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": "connected",
        "llm_provider": settings.LLM_PROVIDER
    }


# Serve built React frontend if dist directory exists
potential_dist_paths = [
    Path("/app/frontend/dist"),
    settings.BASE_DIR.parent / "frontend" / "dist",
    settings.BASE_DIR / "frontend" / "dist",
    settings.BASE_DIR / "dist",
]

dist_dir = next((p for p in potential_dist_paths if p.exists() and (p / "index.html").exists()), None)

if dist_dir:
    from fastapi.responses import FileResponse
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static_assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws") or full_path in ("health", "docs", "openapi.json"):
            return None
        file_path = dist_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
