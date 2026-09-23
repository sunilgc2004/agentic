import pytest
from app.agents.analyzer import ExpectedVsActualAnalyzerAgent
from app.schemas.agent_schemas import GeneratedTestCase, TestStep, StepExecutionResult


@pytest.mark.asyncio
async def test_analyzer_blocked_step():
    test_case = GeneratedTestCase(
        custom_id="TC_TEST_001",
        module="Admin",
        feature="Delete",
        scenario="Delete tenant",
        steps=[],
        expected_result="Tenant deleted."
    )
    step_results = [
        StepExecutionResult(
            step_number=1,
            action="click",
            target="Delete Tenant button",
            status="BLOCKED",
            error="Action restricted in PRODUCTION mode."
        )
    ]
    outcome = await ExpectedVsActualAnalyzerAgent.analyze_outcome(
        test_case=test_case,
        step_results=step_results,
        evidence_summary={},
        final_page_url="http://localhost:8000",
        dom_title="App"
    )
    assert outcome.status == "BLOCKED"
    assert outcome.confidence == 1.0


@pytest.mark.asyncio
async def test_analyzer_failed_step():
    test_case = GeneratedTestCase(
        custom_id="TC_TEST_002",
        module="Cases",
        feature="VC Link",
        scenario="Generate VC Link",
        steps=[],
        expected_result="VC link displayed."
    )
    step_results = [
        StepExecutionResult(
            step_number=1,
            action="click",
            target="Generate VC button",
            status="FAILED",
            error="Element not visible within timeout"
        )
    ]
    outcome = await ExpectedVsActualAnalyzerAgent.analyze_outcome(
        test_case=test_case,
        step_results=step_results,
        evidence_summary={},
        final_page_url="http://localhost:8000",
        dom_title="App"
    )
    assert outcome.status == "FAIL"
