from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import TestSuite, TestCase
from app.schemas.dtos import TestSuiteCreate, TestSuiteResponse, TestCaseResponse

router = APIRouter()


@router.get("", response_model=List[TestSuiteResponse])
def list_test_suites(project_id: str = None, db: Session = Depends(get_db)):
    query = db.query(TestSuite)
    if project_id:
        query = query.filter(TestSuite.project_id == project_id)
    return query.all()


@router.post("", response_model=TestSuiteResponse)
def create_test_suite(data: TestSuiteCreate, db: Session = Depends(get_db)):
    suite = TestSuite(
        project_id=data.project_id,
        name=data.name,
        description=data.description,
        suite_type=data.suite_type
    )
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return suite


@router.get("/{suite_id}/cases", response_model=List[TestCaseResponse])
def get_suite_cases(suite_id: str, db: Session = Depends(get_db)):
    return db.query(TestCase).filter(TestCase.test_suite_id == suite_id).all()
