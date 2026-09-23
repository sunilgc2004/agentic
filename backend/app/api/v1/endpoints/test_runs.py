import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.session import get_db, SessionLocal
from app.models.entities import TestRun, Application, TestResult, Bug, ExecutionLog
from app.schemas.dtos import TestRunCreate, TestRunResponse, HumanInterventionRequest
from app.agents.orchestrator import QAOrchestrator
from app.api.websockets.live_execution import ws_manager

router = APIRouter()


async def execute_run_task(
    run_id: str,
    app_url: str,
    mode: str,
    environment: str,
    browser: str,
    headless: bool,
    credentials: Optional[Dict[str, Any]],
    custom_prompt: Optional[str]
):
    """Background task running the autonomous QA orchestrator."""
    db = SessionLocal()
    try:
        orch = QAOrchestrator(
            db=db,
            test_run_id=run_id,
            application_url=app_url,
            mode=mode,
            environment=environment,
            browser_type=browser,
            headless=headless,
            credentials=credentials,
            custom_prompt=custom_prompt,
            event_broadcaster=lambda msg: ws_manager.broadcast_to_run(run_id, msg)
        )
        await orch.run()
    finally:
        db.close()


@router.post("", response_model=TestRunResponse)
def start_test_run(
    data: TestRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    app = db.query(Application).filter(Application.id == data.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    run_name = data.name or f"{data.mode.capitalize()} Run - {app.name}"

    test_run = TestRun(
        application_id=app.id,
        test_suite_id=data.test_suite_id,
        name=run_name,
        mode=data.mode.upper(),
        environment=data.environment,
        browser=data.browser,
        headless=data.headless,
        status="PENDING"
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)

    # Launch autonomous agent in background task
    background_tasks.add_task(
        execute_run_task,
        run_id=test_run.id,
        app_url=app.base_url,
        mode=data.mode,
        environment=data.environment,
        browser=data.browser,
        headless=data.headless,
        credentials=data.credentials or app.auth_credentials,
        custom_prompt=data.custom_prompt
    )

    return test_run


@router.get("", response_model=List[TestRunResponse])
def list_test_runs(application_id: str = None, db: Session = Depends(get_db)):
    query = db.query(TestRun)
    if application_id:
        query = query.filter(TestRun.application_id == application_id)
    return query.order_by(TestRun.created_at.desc()).all()


@router.get("/{run_id}")
def get_test_run_detail(run_id: str, db: Session = Depends(get_db)):
    test_run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    results = db.query(TestResult).filter(TestResult.test_run_id == run_id).all()
    bugs = db.query(Bug).filter(Bug.test_run_id == run_id).all()
    logs = db.query(ExecutionLog).filter(ExecutionLog.test_run_id == run_id).order_by(ExecutionLog.created_at.asc()).all()

    return {
        "run": test_run,
        "results": results,
        "bugs": bugs,
        "logs": logs[-100:]  # Last 100 logs
    }


@router.post("/{run_id}/control")
async def control_test_run(
    run_id: str,
    data: HumanInterventionRequest,
    db: Session = Depends(get_db)
):
    orch = QAOrchestrator.active_runs.get(run_id)
    if not orch:
        raise HTTPException(status_code=400, detail="Test run is not currently active.")

    action = data.action.lower()
    if action == "pause":
        orch.pause()
        await ws_manager.broadcast_to_run(run_id, {"event": "paused", "run_id": run_id})
    elif action == "resume":
        orch.resume()
        await ws_manager.broadcast_to_run(run_id, {"event": "resumed", "run_id": run_id})
    elif action == "stop":
        orch.stop()
        await ws_manager.broadcast_to_run(run_id, {"event": "stopped", "run_id": run_id})
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported control action: {data.action}")

    return {"status": "SUCCESS", "message": f"Action {action} applied to test run {run_id}"}
