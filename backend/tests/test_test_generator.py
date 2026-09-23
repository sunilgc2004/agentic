import pytest
from app.agents.test_generator import TestCaseGeneratorAgent
from app.schemas.agent_schemas import PageMapSchema, PageElementInfo


@pytest.mark.asyncio
async def test_generate_smoke_suite():
    page_map = PageMapSchema(
        url="http://localhost:8000/api/v1/playground",
        title="Arbitration Portal",
        buttons=[PageElementInfo(tag="button", text="Login", selector="#btn-login")]
    )
    cases = await TestCaseGeneratorAgent.generate_suite(page_map, test_mode="SMOKE")
    assert len(cases) >= 3
    assert any(c.custom_id == "TC_SMOKE_001" for c in cases)
    assert any(c.module == "Authentication" for c in cases)
    assert any(c.module == "Case Management" for c in cases)


@pytest.mark.asyncio
async def test_generate_negative_suite():
    page_map = PageMapSchema(
        url="http://localhost:8000/api/v1/playground",
        title="Arbitration Portal"
    )
    cases = await TestCaseGeneratorAgent.generate_suite(page_map, test_mode="NEGATIVE")
    assert len(cases) >= 2
    assert any(c.test_type == "Negative" for c in cases)
    # Check for SQL injection scenario
    assert any("SQL" in c.scenario for c in cases)


@pytest.mark.asyncio
async def test_generate_from_natural_language():
    page_map = PageMapSchema(url="http://localhost:8000/playground", title="Arbitration Portal")
    prompt = "Verify user can register an arbitration dispute between Apex and Zenith"
    case = await TestCaseGeneratorAgent.generate_from_natural_language(page_map, prompt)
    assert case.custom_id.startswith("TC_")
    assert len(case.steps) > 0
    assert case.expected_result != ""
