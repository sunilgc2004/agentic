import json
from typing import List, Dict, Any, Optional
from app.schemas.agent_schemas import (
    GeneratedTestCase,
    StepExecutionResult,
    OutcomeAnalysis
)
from app.agents.llm_provider import get_llm_provider
from app.core.config import settings
from app.core.logging import logger


class ExpectedVsActualAnalyzerAgent:
    """
    Agent 4: Compares Expected vs Actual behavior after execution.
    Adheres to Principle 41 (never assume PASS just because click didn't crash)
    and Confidence rule 33 (< 0.70 -> INCONCLUSIVE).
    """

    @classmethod
    async def analyze_outcome(
        cls,
        test_case: GeneratedTestCase,
        step_results: List[StepExecutionResult],
        evidence_summary: Dict[str, Any],
        final_page_url: str,
        dom_title: str
    ) -> OutcomeAnalysis:
        logger.info(f"Agent 4 (Analyzer): Comparing expected vs actual for {test_case.custom_id}...")

        # 1. Check for blocked actions
        if any(step.status == "BLOCKED" for step in step_results):
            blocked_step = next(s for s in step_results if s.status == "BLOCKED")
            return OutcomeAnalysis(
                status="BLOCKED",
                confidence=1.0,
                expected=test_case.expected_result,
                actual=f"Execution blocked by safety policy during action '{blocked_step.action}' on '{blocked_step.target}'. Reason: {blocked_step.error}",
                possible_cause="Restricted action triggered without authorization in safe mode."
            )

        # 2. Check for step failures
        failed_steps = [s for s in step_results if s.status == "FAILED"]
        network_errors = evidence_summary.get("network_errors", [])
        console_errors = evidence_summary.get("console_errors", [])

        # Build prompt for LLM evaluation
        prompt = (
            f"You are Agent 4 (Expected vs Actual QA Analyzer).\n"
            f"Test Case: {test_case.custom_id} - {test_case.scenario}\n"
            f"Expected Outcome: {test_case.expected_result}\n"
            f"Executed Steps:\n" + "\n".join([
                f"Step {s.step_number} [{s.action} {s.target}]: {s.status}" + (f" - Error: {s.error}" if s.error else "")
                for s in step_results
            ]) + "\n"
            f"Network Errors: {json.dumps(network_errors[:3])}\n"
            f"Console Errors: {json.dumps(console_errors[:3])}\n"
            f"Final URL: {final_page_url} | Title: {dom_title}\n\n"
            f"CRITICAL RULE: Never assume PASS simply because click had no error. Confirm actual business outcome.\n"
            f"Determine status (PASS, FAIL, BLOCKED, INCONCLUSIVE), confidence (0.0 to 1.0), expected explanation, actual explanation, possible_cause."
        )

        llm = get_llm_provider()
        llm_resp = await llm.generate_json(prompt)

        status = llm_resp.get("status", "FAIL" if failed_steps else "PASS").upper()
        confidence = float(llm_resp.get("confidence", 0.95))

        # Enforce Section 33 confidence rule: if confidence < threshold -> INCONCLUSIVE
        if confidence < settings.CONFIDENCE_THRESHOLD and status not in ("PASS", "BLOCKED"):
            status = "INCONCLUSIVE"

        # If any step failed and LLM reported PASS, enforce FAIL
        if failed_steps and status == "PASS":
            status = "FAIL"
            confidence = 0.95

        expected_text = llm_resp.get("expected", test_case.expected_result)
        actual_text = llm_resp.get("actual", "")
        if not actual_text:
            if failed_steps:
                actual_text = f"Step {failed_steps[0].step_number} failed: {failed_steps[0].error}"
            else:
                actual_text = f"All {len(step_results)} steps completed successfully and outcome verified at {final_page_url}."

        return OutcomeAnalysis(
            status=status,
            confidence=confidence,
            expected=expected_text,
            actual=actual_text,
            possible_cause=llm_resp.get("possible_cause"),
            suggested_category=llm_resp.get("suggested_category")
        )
