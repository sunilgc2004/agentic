from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import Application, Environment
from app.schemas.dtos import ApplicationCreate, ApplicationResponse

router = APIRouter()


@router.post("", response_model=ApplicationResponse)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    app = Application(
        project_id=data.project_id,
        name=data.name,
        base_url=data.base_url,
        description=data.description,
        default_environment=data.default_environment,
        auth_type=data.auth_type,
        auth_credentials=data.auth_credentials
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Initialize default QA environment
    env = Environment(
        application_id=app.id,
        name=data.default_environment,
        url=data.base_url,
        is_safe_mode=(data.default_environment == "production")
    )
    db.add(env)
    db.commit()

    return app


@router.get("", response_model=List[ApplicationResponse])
def list_applications(project_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if project_id:
        query = query.filter(Application.project_id == project_id)
    return query.order_by(Application.created_at.desc()).all()


@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: str, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app
