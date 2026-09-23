from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class PageElementInfo(BaseModel):
    tag: str
    role: Optional[str] = None
    text: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    data_testid: Optional[str] = None
    name: Optional[str] = None
    selector: Optional[str] = None
    is_interactive: bool = True
    input_type: Optional[str] = None


class PageFormInfo(BaseModel):
    form_id: Optional[str] = None
    action: Optional[str] = None
    method: Optional[str] = "POST"
    fields: List[PageElementInfo] = Field(default_factory=list)
    submit_button: Optional[PageElementInfo] = None


class PageMapSchema(BaseModel):
    url: str
    title: str
    routes: List[str] = Field(default_factory=list)
    navigation_links: List[PageElementInfo] = Field(default_factory=list)
    interactive_elements: List[PageElementInfo] = Field(default_factory=list)
    forms: List[PageFormInfo] = Field(default_factory=list)
    buttons: List[PageElementInfo] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    modals: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_workflows: List[str] = Field(default_factory=list)


class TestStep(BaseModel):
    step_number: int
    action: str  # navigate, click, fill, select, assert_visible, assert_text, wait
    target_description: str  # Human readable label e.g. "Username field"
    selector: Optional[str] = None  # Primary locator or hint
    value: Optional[str] = None  # Text to fill or option to select
    expected: Optional[str] = None


class GeneratedTestCase(BaseModel):
    custom_id: str  # e.g. TC_LOGIN_001
    module: str
    feature: str
    scenario: str
    preconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    steps: List[TestStep]
    expected_result: str
    priority: str = "Medium"  # Critical, High, Medium, Low
    test_type: str = "Functional"  # Smoke, Functional, Regression, UI, Negative, Exploratory


class StepExecutionResult(BaseModel):
    step_number: int
    action: str
    target: str
    status: str  # SUCCESS, FAILED, SKIPPED, RETRIED
    duration_ms: float = 0.0
    error: Optional[str] = None
    recovered_selector: Optional[str] = None
    screenshot_path: Optional[str] = None


class OutcomeAnalysis(BaseModel):
    status: str  # PASS, FAIL, BLOCKED, INCONCLUSIVE
    confidence: float = Field(ge=0.0, le=1.0)
    expected: str
    actual: str
    possible_cause: Optional[str] = None
    suggested_category: Optional[str] = None


class BugAnalysisResult(BaseModel):
    custom_id: str
    title: str
    module: str
    severity: str  # Critical, High, Medium, Low
    priority: str  # Critical, High, Medium, Low
    category: str  # Functional, UI, Validation, API, Backend, Frontend, Auth, Performance, Environment, Automation
    steps_to_reproduce: List[str]
    expected_result: str
    actual_result: str
    root_cause_hypothesis: str
    severity_reasoning: str
    is_application_bug: bool = True  # Distinguishes application bugs from automation/environment issues
