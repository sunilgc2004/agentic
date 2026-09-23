import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import TestRun
from app.services.regression_service import RegressionComparisonService
from app.core.config import settings

router = APIRouter()


@router.get("/{run_id}")
def get_report_json(run_id: str, db: Session = Depends(get_db)):
    test_run = db.query(TestRun).filter(TestRun.id == run_id).first()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    report_json_path = settings.REPORTS_DIR / run_id / "report.json"
    if report_json_path.exists():
        return json.loads(report_json_path.read_text(encoding="utf-8"))

    return test_run.summary_report or {"status": "PENDING", "message": "Report compilation in progress."}


@router.get("/{run_id}/html", response_class=HTMLResponse)
def get_report_html(run_id: str, db: Session = Depends(get_db)):
    report_html_path = settings.REPORTS_DIR / run_id / "report.html"
    if not report_html_path.exists():
        raise HTTPException(status_code=404, detail="HTML report not found or run still in progress")
    return HTMLResponse(content=report_html_path.read_text(encoding="utf-8"))


@router.get("/{run_id}/regression")
def get_regression_analysis(run_id: str, baseline_id: str = None, db: Session = Depends(get_db)):
    return RegressionComparisonService.compare_runs(db, run_id, baseline_id)
