import json
from typing import List, Dict, Any, Optional
from app.schemas.agent_schemas import (
    GeneratedTestCase,
    StepExecutionResult,
    OutcomeAnalysis,
    BugAnalysisResult
)
from app.agents.llm_provider import get_llm_provider
from app.core.logging import logger


class BugAnalyzerAgent:
    """
    Agent 5: Root-cause triage, false positive elimination, severity reasoning,
    and structured reproducible bug report generation.
    """

    @classmethod
    async def analyze_failure(
        cls,
        test_case: GeneratedTestCase,
        step_results: List[StepExecutionResult],
        outcome: OutcomeAnalysis,
        evidence_summary: Dict[str, Any],
        application_url: str,
        bug_counter: int = 1
    ) -> BugAnalysisResult:
        logger.info(f"Agent 5 (Bug Analyzer): Triaging failure for {test_case.custom_id}...")

        failed_steps = [s for s in step_results if s.status == "FAILED"]
        primary_error = failed_steps[0].error if failed_steps else outcome.actual

        network_errors = evidence_summary.get("network_errors", [])
        console_errors = evidence_summary.get("console_errors", [])

        # Categorize preliminary failure type (Section 42: Avoid False Positives)
        is_net_conn = any("net::err_" in str(e).lower() or "connection refused" in str(e).lower() for e in [primary_error] + [n.get("error") for n in network_errors])
        has_http_500 = any(n.get("status") in (500, 502, 503, 504) for n in network_errors) or "500" in primary_error
        is_selector_timeout = "could not be located" in primary_error.lower() or "timeout" in primary_error.lower()

        # Build prompt for LLM triage
        prompt = (
            f"You are Agent 5 (Bug & Root Cause Analyzer). Analyze this test failure:\n"
            f"Module: {test_case.module} | Feature: {test_case.feature}\n"
            f"Scenario: {test_case.scenario}\n"
            f"Expected: {test_case.expected_result}\n"
            f"Actual: {outcome.actual}\n"
            f"Failed Step Error: {primary_error}\n"
            f"Network Errors: {json.dumps(network_errors[:3])}\n"
            f"Console Errors: {json.dumps(console_errors[:3])}\n\n"
            f"CRITICAL RULES:\n"
            f"1. Distinguish APPLICATION FAILURE from AUTOMATION/LOCATOR FAILURE from ENVIRONMENT FAILURE.\n"
            f"2. Assign Severity: Critical (system down/major workflow blocked), High (core business broken), Medium (functional bug with workaround), Low (minor UI/cosmetic).\n"
            f"3. Explain why severity was assigned.\n"
            f"Return JSON matching BugAnalysisResult schema."
        )

        llm = get_llm_provider()
        llm_resp = await llm.generate_json(prompt)

        # Establish category & application bug status
        if is_net_conn:
            category = "Environment"
            is_app_bug = False
            severity = "Critical"
            severity_reasoning = "Environment failure: Network unreachable or server host refused connection."
        elif has_http_500:
            category = "API"
            is_app_bug = True
            severity = "High"
            severity_reasoning = "High severity: Backend API failed with HTTP 500 error preventing business action."
        elif is_selector_timeout and not has_http_500:
            category = "Automation"
            is_app_bug = False
            severity = "Low"
            severity_reasoning = "Automation/Locator issue: Element selector failed to match DOM structure; not an application crash."
        else:
            category = llm_resp.get("category", "Functional")
            is_app_bug = llm_resp.get("is_application_bug", True)
            severity = llm_resp.get("severity", "Medium")
            severity_reasoning = llm_resp.get("severity_reasoning", "Assigned based on user impact and available workarounds.")

        title = llm_resp.get("title") or f"{test_case.feature} fails: {primary_error[:80]}"
        steps_to_reproduce = [
            f"1. Open {application_url}",
            f"2. Navigate to {test_case.module} - {test_case.feature}"
        ] + [f"{i+3}. {s.action.capitalize()} {s.target}" for i, s in enumerate(step_results)]

        bug_id = f"BUG-{str(bug_counter).zfill(3)}"

        return BugAnalysisResult(
            custom_id=bug_id,
            title=title,
            module=test_case.module,
            severity=severity,
            priority=llm_resp.get("priority", "High" if severity in ("Critical", "High") else "Medium"),
            category=category,
            steps_to_reproduce=steps_to_reproduce,
            expected_result=test_case.expected_result,
            actual_result=outcome.actual,
            root_cause_hypothesis=llm_resp.get("root_cause_hypothesis", "Potential functional or API failure detected during automated execution."),
            severity_reasoning=severity_reasoning,
            is_application_bug=is_app_bug
        )
