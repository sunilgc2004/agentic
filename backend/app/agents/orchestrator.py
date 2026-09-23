import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session

from app.models.entities import (
    TestRun, TestCase, TestResult, Bug, ExecutionLog, ApiLog, Screenshot, Application
)
from app.agents.state_machine import AgentStateMachine, AgentState
from app.agents.explorer import ApplicationExplorerAgent
from app.agents.test_generator import TestCaseGeneratorAgent
from app.agents.executor import BrowserExecutionAgent
from app.agents.analyzer import ExpectedVsActualAnalyzerAgent
from app.agents.bug_analyzer import BugAnalyzerAgent
from app.browser.manager import BrowserManager
from app.browser.evidence_collector import EvidenceCollector
from app.browser.performance import PerformanceMonitor
from app.services.report_generator import ReportGeneratorService
from app.core.logging import logger, StructuredLogger


class QAOrchestrator:
    """
    Coordinates end-to-end autonomous QA testing across the 5 specialized agents,
    enforcing finite state transitions and live WebSocket telemetry.
    """

    # Global registry for active runs to support Pause/Resume/Stop
    active_runs: Dict[str, "QAOrchestrator"] = {}

    def __init__(
        self,
        db: Session,
        test_run_id: str,
        application_url: str,
        mode: str = "SMOKE",
        environment: str = "qa",
        browser_type: str = "chromium",
        headless: bool = True,
        credentials: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
        event_broadcaster: Optional[Callable] = None
    ):
        self.db = db
        self.run_id = test_run_id
        self.app_url = application_url
        self.mode = mode.upper()
        self.environment = environment
        self.browser_type = browser_type
        self.headless = headless
        self.credentials = credentials or {}
        self.custom_prompt = custom_prompt
        self.broadcaster = event_broadcaster

        self.state_machine = AgentStateMachine()
        self.browser_manager = BrowserManager(browser_type=browser_type, headless=headless)
        self.evidence_collector = EvidenceCollector(run_id=test_run_id)
        self.performance_monitor = PerformanceMonitor()

        self.is_paused = False
        self.is_stopped = False
        self.pending_human_approval = False
        self.human_decision: Optional[str] = None

        QAOrchestrator.active_runs[test_run_id] = self

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Emits event to WebSocket listeners safely handling coroutines or sync callables."""
        if self.broadcaster:
            try:
                res = self.broadcaster({
                    "run_id": self.run_id,
                    "event": event_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data
                })
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                logger.error(f"Error broadcasting event {event_type}: {e}")

    async def run(self):
        start_time = time.time()
        test_run = self.db.query(TestRun).filter(TestRun.id == self.run_id).first()
        if not test_run:
            logger.error(f"TestRun {self.run_id} not found in database.")
            return

        test_run.status = "RUNNING"
        test_run.started_at = datetime.utcnow()
        self.db.commit()

        await self.broadcast("status_changed", {"status": "RUNNING", "state": "INITIALIZING"})

        page = None
        try:
            # 1. BROWSER INITIALIZATION
            page = await self.browser_manager.initialize()
            self.evidence_collector.attach_listeners(page)

            # 2. DISCOVER
            self.state_machine.transition_to(AgentState.DISCOVER, "Crawling page DOM")
            await self.broadcast("state_transition", {"state": "DISCOVER", "message": f"Exploring {self.app_url}"})
            page_map = await ApplicationExplorerAgent.explore_page(page, self.app_url)

            # 3. PLAN
            self.state_machine.transition_to(AgentState.PLAN, "Generating test scenarios")
            await self.broadcast("state_transition", {"state": "PLAN", "message": f"Generating {self.mode} test cases"})
            test_cases = await TestCaseGeneratorAgent.generate_suite(
                page_map=page_map,
                test_mode=self.mode,
                credentials=self.credentials,
                custom_prompt=self.custom_prompt
            )

            # 4. VALIDATE PLAN
            self.state_machine.transition_to(AgentState.VALIDATE_PLAN, "Verifying safety and preconditions")
            await self.broadcast("state_transition", {"state": "VALIDATE_PLAN", "total_cases": len(test_cases)})

            # Sync test cases into database
            db_case_map = {}
            for tc in test_cases:
                existing_tc = self.db.query(TestCase).filter(
                    TestCase.application_id == test_run.application_id,
                    TestCase.custom_id == tc.custom_id
                ).first()
                if not existing_tc:
                    existing_tc = TestCase(
                        application_id=test_run.application_id,
                        test_suite_id=test_run.test_suite_id,
                        custom_id=tc.custom_id,
                        module=tc.module,
                        feature=tc.feature,
                        scenario=tc.scenario,
                        preconditions=tc.preconditions,
                        test_data=tc.test_data,
                        steps=[s.dict() for s in tc.steps],
                        expected_result=tc.expected_result,
                        priority=tc.priority,
                        test_type=tc.test_type
                    )
                    self.db.add(existing_tc)
                    self.db.commit()
                    self.db.refresh(existing_tc)
                db_case_map[tc.custom_id] = existing_tc.id

            test_run.total_tests = len(test_cases)
            self.db.commit()

            passed_count = 0
            failed_count = 0
            blocked_count = 0
            inconclusive_count = 0
            bug_counter = 1

            # 5. EXECUTION LOOP
            for idx, tc in enumerate(test_cases):
                if self.is_stopped:
                    logger.info("Test execution stopped by user command.")
                    break

                while self.is_paused:
                    await asyncio.sleep(1)

                logger.info(f"Executing Test {idx+1}/{len(test_cases)}: {tc.custom_id}")
                await self.broadcast("test_started", {
                    "test_id": tc.custom_id,
                    "scenario": tc.scenario,
                    "index": idx + 1,
                    "total": len(test_cases)
                })

                # State: EXECUTE
                self.state_machine.transition_to(AgentState.EXECUTE, f"Running {tc.custom_id}")
                
                async def on_step(step_res):
                    await self.broadcast("step_update", {
                        "test_id": tc.custom_id,
                        "step": step_res.dict()
                    })

                executor_agent = BrowserExecutionAgent(
                    page=page,
                    evidence_collector=self.evidence_collector,
                    run_id=self.run_id,
                    environment=self.environment,
                    on_step_update=on_step
                )

                test_case_start = time.time()
                step_results, failure_screenshot = await executor_agent.execute_test_case(tc)
                duration_ms = (time.time() - test_case_start) * 1000

                # State: OBSERVE & ANALYZE
                self.state_machine.transition_to(AgentState.OBSERVE, "Gathering telemetry")
                evidence_summary = self.evidence_collector.get_summary_evidence()
                current_url = page.url
                page_title = await page.title()

                self.state_machine.transition_to(AgentState.ANALYZE, "Evaluating outcome")
                outcome = await ExpectedVsActualAnalyzerAgent.analyze_outcome(
                    test_case=tc,
                    step_results=step_results,
                    evidence_summary=evidence_summary,
                    final_page_url=current_url,
                    dom_title=page_title
                )

                # State: RECOVER & RETRY if failure and retries remain
                retries_used = 0
                if outcome.status == "FAIL" and self.state_machine.can_retry():
                    self.state_machine.transition_to(AgentState.RECOVER, "Attempting retry")
                    self.state_machine.record_retry()
                    retries_used += 1
                    await self.broadcast("test_retried", {"test_id": tc.custom_id, "retry_count": retries_used})
                    step_results, failure_screenshot = await executor_agent.execute_test_case(tc)
                    outcome = await ExpectedVsActualAnalyzerAgent.analyze_outcome(
                        test_case=tc,
                        step_results=step_results,
                        evidence_summary=self.evidence_collector.get_summary_evidence(),
                        final_page_url=page.url,
                        dom_title=await page.title()
                    )

                self.state_machine.reset_retry()

                # Tally metrics
                if outcome.status == "PASS":
                    passed_count += 1
                elif outcome.status == "FAIL":
                    failed_count += 1
                elif outcome.status == "BLOCKED":
                    blocked_count += 1
                else:
                    inconclusive_count += 1

                # Save TestResult to DB
                db_result = TestResult(
                    test_run_id=self.run_id,
                    test_case_id=db_case_map[tc.custom_id],
                    status=outcome.status,
                    confidence=outcome.confidence,
                    expected_result=outcome.expected,
                    actual_result=outcome.actual,
                    error_message=step_results[-1].error if step_results and step_results[-1].error else None,
                    failure_category=outcome.suggested_category,
                    execution_duration_ms=round(duration_ms, 2),
                    retries_used=retries_used,
                    step_results=[s.dict() for s in step_results],
                    screenshot_path=failure_screenshot
                )
                self.db.add(db_result)
                self.db.commit()
                self.db.refresh(db_result)

                # If FAIL, trigger Agent 5 (Bug Analyzer)
                if outcome.status == "FAIL":
                    bug_analysis = await BugAnalyzerAgent.analyze_failure(
                        test_case=tc,
                        step_results=step_results,
                        outcome=outcome,
                        evidence_summary=evidence_summary,
                        application_url=self.app_url,
                        bug_counter=bug_counter
                    )
                    bug_counter += 1

                    db_bug = Bug(
                        custom_id=bug_analysis.custom_id,
                        test_run_id=self.run_id,
                        test_result_id=db_result.id,
                        title=bug_analysis.title,
                        module=bug_analysis.module,
                        severity=bug_analysis.severity,
                        priority=bug_analysis.priority,
                        category=bug_analysis.category,
                        environment=self.environment,
                        application_url=self.app_url,
                        steps_to_reproduce=bug_analysis.steps_to_reproduce,
                        expected_result=bug_analysis.expected_result,
                        actual_result=bug_analysis.actual_result,
                        root_cause_hypothesis=bug_analysis.root_cause_hypothesis,
                        severity_reasoning=bug_analysis.severity_reasoning,
                        evidence={
                            "screenshot": failure_screenshot,
                            "network_errors": evidence_summary.get("network_errors", []),
                            "console_errors": evidence_summary.get("console_errors", [])
                        }
                    )
                    self.db.add(db_bug)
                    self.db.commit()

                    await self.broadcast("bug_detected", {
                        "bug_id": db_bug.custom_id,
                        "title": db_bug.title,
                        "severity": db_bug.severity,
                        "category": db_bug.category
                    })

                await self.broadcast("test_completed", {
                    "test_id": tc.custom_id,
                    "status": outcome.status,
                    "confidence": outcome.confidence,
                    "duration_ms": duration_ms
                })

            # 6. REPORT GENERATION
            self.state_machine.transition_to(AgentState.REPORT, "Compiling executive report")
            total_duration = time.time() - start_time
            pass_percentage = round((passed_count / len(test_cases) * 100), 1) if test_cases else 0.0

            test_run.status = "COMPLETED" if not self.is_stopped else "STOPPED"
            test_run.passed_tests = passed_count
            test_run.failed_tests = failed_count
            test_run.blocked_tests = blocked_count
            test_run.inconclusive_tests = inconclusive_count
            test_run.pass_percentage = pass_percentage
            test_run.duration_seconds = round(total_duration, 2)
            test_run.completed_at = datetime.utcnow()

            # Compile report
            results_list = []
            for tc in test_cases:
                res = self.db.query(TestResult).filter(
                    TestResult.test_run_id == self.run_id,
                    TestResult.test_case_id == db_case_map[tc.custom_id]
                ).first()
                if res:
                    results_list.append({
                        "custom_id": tc.custom_id,
                        "scenario": tc.scenario,
                        "module": tc.module,
                        "status": res.status,
                        "confidence": res.confidence,
                        "duration_ms": res.execution_duration_ms
                    })

            bugs_list = []
            for b in self.db.query(Bug).filter(Bug.test_run_id == self.run_id).all():
                bugs_list.append({
                    "custom_id": b.custom_id,
                    "title": b.title,
                    "module": b.module,
                    "severity": b.severity,
                    "category": b.category,
                    "expected_result": b.expected_result,
                    "actual_result": b.actual_result,
                    "root_cause_hypothesis": b.root_cause_hypothesis,
                    "severity_reasoning": b.severity_reasoning,
                    "steps_to_reproduce": b.steps_to_reproduce
                })

            summary_dict = {
                "run_id": self.run_id,
                "run_name": test_run.name,
                "app_name": test_run.application.name if test_run.application else "Application",
                "app_url": self.app_url,
                "mode": self.mode,
                "environment": self.environment,
                "total_tests": len(test_cases),
                "passed_tests": passed_count,
                "failed_tests": failed_count,
                "blocked_tests": blocked_count,
                "inconclusive_tests": inconclusive_count,
                "pass_percentage": pass_percentage,
                "duration_seconds": round(total_duration, 2),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            reports = ReportGeneratorService.generate_reports(summary_dict, results_list, bugs_list)
            test_run.summary_report = {**summary_dict, "reports": reports}
            self.db.commit()

            self.state_machine.transition_to(AgentState.COMPLETED, "Autonomous QA run finished")
            await self.broadcast("run_completed", summary_dict)

        except Exception as e:
            logger.exception(f"Unhandled error in QA Orchestrator: {e}")
            self.state_machine.transition_to(AgentState.FAILED, str(e))
            test_run.status = "FAILED"
            test_run.summary_report = {"status": "FAILED", "error": str(e)}
            
            # Log error in execution logs table
            err_log = ExecutionLog(
                test_run_id=self.run_id,
                agent="Orchestrator",
                action="SYSTEM_ERROR",
                target=self.app_url,
                result="FAILED",
                error=str(e),
                duration_ms=round((time.time() - start_time) * 1000, 2)
            )
            self.db.add(err_log)
            self.db.commit()
            
            await self.broadcast("run_failed", {"error": str(e), "message": f"Execution failed: {str(e)}"})

        finally:
            await self.browser_manager.close()
            QAOrchestrator.active_runs.pop(self.run_id, None)

    # Human-in-the-Loop Controls
    def pause(self):
        self.is_paused = True
        logger.info(f"Orchestrator {self.run_id} PAUSED.")

    def resume(self):
        self.is_paused = False
        logger.info(f"Orchestrator {self.run_id} RESUMED.")

    def stop(self):
        self.is_stopped = True
        self.is_paused = False
        logger.info(f"Orchestrator {self.run_id} STOPPED.")
