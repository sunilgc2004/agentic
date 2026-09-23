import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.entities import Project, Application, TestRun, Bug, TestResult
from app.agents.orchestrator import QAOrchestrator
from app.main import seed_initial_data


async def main():
    print("=== Running Autonomous AI QA Agent Verification ===")
    Base.metadata.create_all(bind=engine)
    seed_initial_data()

    db = SessionLocal()
    try:
        app = db.query(Application).first()
        if not app:
            print("ERROR: No seeded application found.")
            return

        print(f"Target Application: {app.name} ({app.base_url})")

        # Create a Test Run
        test_run = TestRun(
            application_id=app.id,
            name="Verification Smoke Run",
            mode="SMOKE",
            environment="qa",
            browser="chromium",
            headless=True,
            status="PENDING"
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)

        print(f"Created TestRun ID: {test_run.id}")

        async def broadcast_event(msg):
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "state_transition":
                print(f"  [STATE] {data.get('state')}: {data.get('message', '')}")
            elif event == "test_started":
                print(f"  [TEST START] {data.get('test_id')}: {data.get('scenario')}")
            elif event == "step_update":
                step = data.get("step", {})
                print(f"    -> Step {step.get('step_number')}: {step.get('action')} on {step.get('target')} - {step.get('status')}")
            elif event == "bug_detected":
                print(f"  [BUG FOUND] {data.get('bug_id')}: {data.get('title')} (Severity: {data.get('severity')})")
            elif event == "run_completed":
                print(f"  [RUN COMPLETED] Pass rate: {data.get('pass_percentage')}% | Tests: {data.get('total_tests')}")

        orch = QAOrchestrator(
            db=db,
            test_run_id=test_run.id,
            application_url=app.base_url,
            mode="SMOKE",
            environment="qa",
            browser_type="chromium",
            headless=True,
            credentials=app.auth_credentials,
            event_broadcaster=broadcast_event
        )

        print("Starting Autonomous QA Orchestrator...")
        await orch.run()

        # Check outcomes in DB
        db.refresh(test_run)
        print("\n=== Final Verification Results ===")
        print(f"Status: {test_run.status}")
        print(f"Total Tests: {test_run.total_tests}")
        print(f"Passed Tests: {test_run.passed_tests}")
        print(f"Failed Tests: {test_run.failed_tests}")
        print(f"Pass %: {test_run.pass_percentage}%")
        print(f"Duration: {test_run.duration_seconds}s")

        results = db.query(TestResult).filter(TestResult.test_run_id == test_run.id).all()
        print(f"Recorded Test Results in DB: {len(results)}")

        bugs = db.query(Bug).filter(Bug.test_run_id == test_run.id).all()
        print(f"Recorded Bugs in DB: {len(bugs)}")
        for b in bugs:
            print(f"  * {b.custom_id} [{b.severity}]: {b.title} (Reason: {b.severity_reasoning})")

        report_summary = test_run.summary_report or {}
        reports = report_summary.get("reports", {})
        html_path = reports.get("html_path")
        json_path = reports.get("json_path")
        print(f"HTML Report generated: {html_path} (Exists: {os.path.exists(html_path) if html_path else False})")
        print(f"JSON Report generated: {json_path} (Exists: {os.path.exists(json_path) if json_path else False})")

        assert test_run.status == "COMPLETED"
        assert len(results) > 0
        print("\nSUCCESS: All end-to-end Autonomous QA Agent verification checks passed!")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
