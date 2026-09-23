from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.agent_schemas import TestStep, GeneratedTestCase


# Project DTOs
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Application DTOs
class ApplicationCreate(BaseModel):
    project_id: str
    name: str
    base_url: str
    description: Optional[str] = None
    default_environment: str = "qa"
    auth_type: str = "none"  # none, credentials, token
    auth_credentials: Optional[Dict[str, Any]] = None


class ApplicationResponse(BaseModel):
    id: str
    project_id: str
    name: str
    base_url: str
    description: Optional[str]
    default_environment: str
    auth_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Test Case DTOs
class TestCaseCreate(BaseModel):
    application_id: str
    test_suite_id: Optional[str] = None
    custom_id: str
    module: str
    feature: str
    scenario: str
    preconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    steps: List[TestStep]
    expected_result: str
    priority: str = "Medium"
    test_type: str = "Functional"
    tags: List[str] = Field(default_factory=list)
    is_enabled: bool = True


class TestCaseUpdate(BaseModel):
    module: Optional[str] = None
    feature: Optional[str] = None
    scenario: Optional[str] = None
    preconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    steps: Optional[List[TestStep]] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    test_type: Optional[str] = None
    tags: Optional[List[str]] = None
    is_enabled: Optional[bool] = None


class TestCaseResponse(BaseModel):
    id: str
    application_id: str
    test_suite_id: Optional[str]
    custom_id: str
    module: str
    feature: str
    scenario: str
    preconditions: Optional[str]
    test_data: Optional[Dict[str, Any]]
    steps: List[Any]
    expected_result: str
    priority: str
    test_type: str
    tags: List[str]
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Test Suite DTOs
class TestSuiteCreate(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    suite_type: str = "smoke"


class TestSuiteResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str]
    suite_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Test Run DTOs
class TestRunCreate(BaseModel):
    application_id: str
    test_suite_id: Optional[str] = None
    name: Optional[str] = None
    mode: str = "SMOKE"  # SMOKE, FUNCTIONAL, REGRESSION, UI, NEGATIVE, EXPLORATORY, FULL_QA
    environment: str = "qa"
    browser: str = "chromium"
    headless: bool = True
    credentials: Optional[Dict[str, Any]] = None
    custom_prompt: Optional[str] = None  # Natural language instruction if any


class TestResultResponse(BaseModel):
    id: str
    test_case_id: str
    status: str
    confidence: float
    expected_result: Optional[str]
    actual_result: Optional[str]
    error_message: Optional[str]
    failure_category: Optional[str]
    execution_duration_ms: float
    retries_used: int
    step_results: List[Any]
    screenshot_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BugResponse(BaseModel):
    id: str
    custom_id: str
    test_run_id: str
    title: str
    module: str
    severity: str
    priority: str
    category: str
    environment: str
    application_url: str
    steps_to_reproduce: List[Any]
    expected_result: str
    actual_result: str
    root_cause_hypothesis: str
    severity_reasoning: str
    evidence: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BugUpdate(BaseModel):
    status: Optional[str] = None  # OPEN, FALSE_POSITIVE, RESOLVED
    severity: Optional[str] = None
    priority: Optional[str] = None


class TestRunResponse(BaseModel):
    id: str
    application_id: str
    test_suite_id: Optional[str]
    name: str
    status: str
    mode: str
    environment: str
    browser: str
    headless: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    blocked_tests: int
    inconclusive_tests: int
    pass_percentage: float
    duration_seconds: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    summary_report: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class ExecutionLogResponse(BaseModel):
    id: str
    test_run_id: str
    test_id: Optional[str]
    agent: str
    action: str
    target: str
    result: str
    duration_ms: float
    error: Optional[str]
    log_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class NaturalLanguageTestRequest(BaseModel):
    application_id: str
    prompt: str  # e.g. "Verify user can create a new arbitration case using valid claimant..."
    module: Optional[str] = "Case Management"
    priority: Optional[str] = "High"


class HumanInterventionRequest(BaseModel):
    action: str  # pause, resume, stop, approve, reject
    notes: Optional[str] = None
