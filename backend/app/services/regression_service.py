from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.entities import TestRun, TestResult


class RegressionComparisonService:
    """Compares current test execution results against a baseline historical run."""

    @staticmethod
    def compare_runs(db: Session, current_run_id: str, baseline_run_id: str = None) -> Dict[str, Any]:
        current_results = db.query(TestResult).filter(TestResult.test_run_id == current_run_id).all()
        
        # If baseline not explicitly passed, pick the most recent completed run before this one
        if not baseline_run_id:
            curr_run = db.query(TestRun).filter(TestRun.id == current_run_id).first()
            if curr_run:
                prev_run = db.query(TestRun).filter(
                    TestRun.application_id == curr_run.application_id,
                    TestRun.id != current_run_id,
                    TestRun.status == "COMPLETED"
                ).order_by(TestRun.created_at.desc()).first()
                if prev_run:
                    baseline_run_id = prev_run.id

        if not baseline_run_id:
            return {
                "has_baseline": False,
                "message": "No previous baseline test run found for comparison."
            }

        prev_results = db.query(TestResult).filter(TestResult.test_run_id == baseline_run_id).all()
        prev_map = {r.test_case_id: r.status for r in prev_results}

        newly_failed = []  # Previously Passed -> Now Failed (REGRESSION)
        fixed_tests = []   # Previously Failed -> Now Passed (FIXED)
        stable_passed = [] # Passed -> Passed
        stable_failed = [] # Failed -> Failed

        for curr in current_results:
            tc_id = curr.test_case_id
            curr_status = curr.status
            prev_status = prev_map.get(tc_id)

            item = {
                "test_case_id": tc_id,
                "current_status": curr_status,
                "previous_status": prev_status
            }

            if prev_status == "PASS" and curr_status == "FAIL":
                newly_failed.append(item)
            elif prev_status == "FAIL" and curr_status == "PASS":
                fixed_tests.append(item)
            elif prev_status == "PASS" and curr_status == "PASS":
                stable_passed.append(item)
            elif prev_status == "FAIL" and curr_status == "FAIL":
                stable_failed.append(item)

        return {
            "has_baseline": True,
            "baseline_run_id": baseline_run_id,
            "summary": {
                "newly_failed_count": len(newly_failed),
                "fixed_count": len(fixed_tests),
                "stable_passed_count": len(stable_passed),
                "stable_failed_count": len(stable_failed)
            },
            "newly_failed": newly_failed,
            "fixed_tests": fixed_tests,
            "stable_passed": stable_passed,
            "stable_failed": stable_failed
        }
