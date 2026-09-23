import pytest
from app.agents.bug_analyzer import BugAnalyzerAgent
from app.schemas.agent_schemas import GeneratedTestCase, StepExecutionResult, OutcomeAnalysis


@pytest.mark.asyncio
async def test_bug_analyzer_http_500():
    test_case = GeneratedTestCase(
        custom_id="TC_SMOKE_003",
        module="Case Management",
        feature="Generate VC Link",
        scenario="Generate VC Link",
        steps=[],
        expected_result="VC link generated."
    )
    step_results = [
        StepExecutionResult(
            step_number=1,
            action="click",
            target="Generate VC Link button",
            status="FAILED",
            error="HTTP 500 Internal Server Error returned by /api/cases/vc-token"
        )
    ]
    outcome = OutcomeAnalysis(
        status="FAIL",
        confidence=0.95,
        expected="VC link should be generated",
        actual="Button was clicked but server returned HTTP 500"
    )
    evidence = {
        "network_errors": [{"url": "/api/cases/vc-token", "status": 500}],
        "console_errors": []
    }

    bug = await BugAnalyzerAgent.analyze_failure(
        test_case=test_case,
        step_results=step_results,
        outcome=outcome,
        evidence_summary=evidence,
        application_url="http://localhost:8000/api/v1/playground",
        bug_counter=1
    )

    assert bug.custom_id == "BUG-001"
    assert bug.category == "API"
    assert bug.severity == "High"
    assert bug.is_application_bug is True


@pytest.mark.asyncio
async def test_bug_analyzer_distinguishes_automation_issue():
    test_case = GeneratedTestCase(
        custom_id="TC_UI_002",
        module="UI",
        feature="Header",
        scenario="Verify old logo",
        steps=[],
        expected_result="Logo visible."
    )
    step_results = [
        StepExecutionResult(
            step_number=1,
            action="click",
            target="#old-logo-button",
            status="FAILED",
            error="Element '#old-logo-button' could not be located using priority selectors or self-healing."
        )
    ]
    outcome = OutcomeAnalysis(
        status="FAIL",
        confidence=0.95,
        expected="Logo should be clicked",
        actual="Element not found"
    )
    evidence = {"network_errors": [], "console_errors": []}

    bug = await BugAnalyzerAgent.analyze_failure(
        test_case=test_case,
        step_results=step_results,
        outcome=outcome,
        evidence_summary=evidence,
        application_url="http://localhost:8000",
        bug_counter=2
    )

    # Must be categorized as Automation issue, NOT application bug
    assert bug.category == "Automation"
    assert bug.is_application_bug is False
    assert bug.severity == "Low"
