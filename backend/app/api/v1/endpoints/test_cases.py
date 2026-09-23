from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import TestCase, Application
from app.schemas.dtos import (
    TestCaseCreate, TestCaseUpdate, TestCaseResponse, NaturalLanguageTestRequest
)
from app.agents.test_generator import TestCaseGeneratorAgent
from app.schemas.agent_schemas import PageMapSchema

router = APIRouter()


@router.get("", response_model=List[TestCaseResponse])
def list_test_cases(
    application_id: Optional[str] = None,
    module: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TestCase)
    if application_id:
        query = query.filter(TestCase.application_id == application_id)
    if module:
        query = query.filter(TestCase.module == module)
    if priority:
        query = query.filter(TestCase.priority == priority)
    return query.order_by(TestCase.created_at.desc()).all()


@router.post("", response_model=TestCaseResponse)
def create_test_case(data: TestCaseCreate, db: Session = Depends(get_db)):
    tc = TestCase(
        application_id=data.application_id,
        test_suite_id=data.test_suite_id,
        custom_id=data.custom_id,
        module=data.module,
        feature=data.feature,
        scenario=data.scenario,
        preconditions=data.preconditions,
        test_data=data.test_data,
        steps=[s.dict() for s in data.steps],
        expected_result=data.expected_result,
        priority=data.priority,
        test_type=data.test_type,
        tags=data.tags,
        is_enabled=data.is_enabled
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


@router.put("/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(test_case_id: str, data: TestCaseUpdate, db: Session = Depends(get_db)):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    for key, value in data.dict(exclude_unset=True).items():
        if key == "steps" and value is not None:
            setattr(tc, key, [s.dict() if hasattr(s, "dict") else s for s in value])
        else:
            setattr(tc, key, value)

    db.commit()
    db.refresh(tc)
    return tc


@router.delete("/{test_case_id}")
def delete_test_case(test_case_id: str, db: Session = Depends(get_db)):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    db.delete(tc)
    db.commit()
    return {"status": "DELETED", "id": test_case_id}


@router.post("/natural-language", response_model=TestCaseResponse)
async def generate_from_natural_language(
    data: NaturalLanguageTestRequest,
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == data.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    mock_map = PageMapSchema(url=app.base_url, title=app.name)
    generated = await TestCaseGeneratorAgent.generate_from_natural_language(mock_map, data.prompt)

    # Save to database
    tc = TestCase(
        application_id=app.id,
        custom_id=generated.custom_id,
        module=data.module or generated.module,
        feature=generated.feature,
        scenario=generated.scenario,
        preconditions=generated.preconditions,
        test_data=generated.test_data,
        steps=[s.dict() for s in generated.steps],
        expected_result=generated.expected_result,
        priority=data.priority or generated.priority,
        test_type="Custom",
        tags=["ai-generated", "natural-language"]
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc
