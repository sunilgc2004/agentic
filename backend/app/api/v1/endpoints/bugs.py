from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import Bug
from app.schemas.dtos import BugResponse, BugUpdate

router = APIRouter()


@router.get("", response_model=List[BugResponse])
def list_bugs(
    test_run_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Bug)
    if test_run_id:
        query = query.filter(Bug.test_run_id == test_run_id)
    if severity:
        query = query.filter(Bug.severity == severity)
    if status:
        query = query.filter(Bug.status == status)
    return query.order_by(Bug.created_at.desc()).all()


@router.get("/{bug_id}", response_model=BugResponse)
def get_bug(bug_id: str, db: Session = Depends(get_db)):
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


@router.patch("/{bug_id}", response_model=BugResponse)
def update_bug(bug_id: str, data: BugUpdate, db: Session = Depends(get_db)):
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    if data.status:
        bug.status = data.status
    if data.severity:
        bug.severity = data.severity
    if data.priority:
        bug.priority = data.priority

    db.commit()
    db.refresh(bug)
    return bug
