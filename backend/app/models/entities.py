import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="qa_engineer")
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    applications = relationship("Application", back_populates="project", cascade="all, delete-orphan")
    test_suites = relationship("TestSuite", back_populates="project", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    base_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    default_environment = Column(String(50), default="qa")
    auth_type = Column(String(50), default="credentials")  # none, credentials, token, session
    auth_credentials = Column(JSON, nullable=True)  # encrypted / masked in responses
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="applications")
    environments = relationship("Environment", back_populates="application", cascade="all, delete-orphan")
    test_runs = relationship("TestRun", back_populates="application", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="application", cascade="all, delete-orphan")


class Environment(Base):
    __tablename__ = "environments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    name = Column(String(50), nullable=False)  # local, development, qa, staging, production
    url = Column(String(500), nullable=False)
    is_safe_mode = Column(Boolean, default=False)  # If true or production, destructive actions blocked
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="environments")


class TestSuite(Base):
    __tablename__ = "test_suites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    suite_type = Column(String(50), default="smoke")  # smoke, functional, regression, exploratory, negative, full_qa
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="test_suites")
    test_cases = relationship("TestCase", back_populates="test_suite")
    test_runs = relationship("TestRun", back_populates="test_suite")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    test_suite_id = Column(String(36), ForeignKey("test_suites.id"), nullable=True)
    custom_id = Column(String(50), index=True, nullable=False)  # e.g. TC_LOGIN_001
    module = Column(String(100), nullable=False)
    feature = Column(String(100), nullable=False)
    scenario = Column(String(255), nullable=False)
    preconditions = Column(Text, nullable=True)
    test_data = Column(JSON, nullable=True)
    steps = Column(JSON, nullable=False)  # List of action steps
    expected_result = Column(Text, nullable=False)
    priority = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    test_type = Column(String(50), default="Functional")  # Smoke, Functional, Regression, UI, Negative, Exploratory
    tags = Column(JSON, default=list)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    application = relationship("Application", back_populates="test_cases")
    test_suite = relationship("TestSuite", back_populates="test_cases")
    test_results = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    test_suite_id = Column(String(36), ForeignKey("test_suites.id"), nullable=True)
    name = Column(String(255), nullable=False)
    status = Column(String(30), default="PENDING")  # PENDING, RUNNING, PAUSED, COMPLETED, STOPPED, FAILED
    mode = Column(String(50), default="SMOKE")  # SMOKE, FUNCTIONAL, REGRESSION, UI, NEGATIVE, EXPLORATORY, FULL_QA
    environment = Column(String(50), default="qa")
    browser = Column(String(30), default="chromium")
    headless = Column(Boolean, default=True)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    blocked_tests = Column(Integer, default=0)
    inconclusive_tests = Column(Integer, default=0)
    pass_percentage = Column(Float, default=0.0)
    duration_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary_report = Column(JSON, nullable=True)

    application = relationship("Application", back_populates="test_runs")
    test_suite = relationship("TestSuite", back_populates="test_runs")
    test_results = relationship("TestResult", back_populates="test_run", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="test_run", cascade="all, delete-orphan")
    execution_logs = relationship("ExecutionLog", back_populates="test_run", cascade="all, delete-orphan")
    api_logs = relationship("ApiLog", back_populates="test_run", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="test_run", cascade="all, delete-orphan")
    browser_sessions = relationship("BrowserSession", back_populates="test_run", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_case_id = Column(String(36), ForeignKey("test_cases.id"), nullable=False)
    status = Column(String(20), nullable=False)  # PASS, FAIL, BLOCKED, INCONCLUSIVE
    confidence = Column(Float, default=1.0)
    expected_result = Column(Text, nullable=True)
    actual_result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    failure_category = Column(String(50), nullable=True)  # APPLICATION_BUG, AUTOMATION_FAILURE, ENVIRONMENT_FAILURE, TEST_DATA_FAILURE
    execution_duration_ms = Column(Float, default=0.0)
    retries_used = Column(Integer, default=0)
    step_results = Column(JSON, default=list)  # Detail of each step executed
    screenshot_path = Column(String(500), nullable=True)
    dom_snapshot_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="test_results")
    test_case = relationship("TestCase", back_populates="test_results")
    bug = relationship("Bug", back_populates="test_result", uselist=False)


class Bug(Base):
    __tablename__ = "bugs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    custom_id = Column(String(50), index=True, nullable=False)  # BUG-001
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_result_id = Column(String(36), ForeignKey("test_results.id"), nullable=True)
    title = Column(String(255), nullable=False)
    module = Column(String(100), nullable=False)
    severity = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    priority = Column(String(20), default="Medium")  # Critical, High, Medium, Low
    category = Column(String(50), nullable=False)  # Functional, UI, Validation, API, Backend, Frontend, Auth, Performance
    environment = Column(String(50), default="qa")
    application_url = Column(String(500), nullable=False)
    steps_to_reproduce = Column(JSON, default=list)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    root_cause_hypothesis = Column(Text, nullable=False)
    severity_reasoning = Column(Text, nullable=False)
    evidence = Column(JSON, default=dict)  # screenshots, console logs, network error info
    status = Column(String(30), default="OPEN")  # OPEN, FALSE_POSITIVE, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="bugs")
    test_result = relationship("TestResult", back_populates="bug")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_id = Column(String(50), nullable=True)
    agent = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    target = Column(String(500), nullable=False)
    result = Column(String(50), nullable=False)
    duration_ms = Column(Float, default=0.0)
    error = Column(Text, nullable=True)
    log_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="execution_logs")


class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_id = Column(String(50), nullable=True)
    method = Column(String(10), nullable=False)
    url = Column(String(1000), nullable=False)
    status_code = Column(Integer, nullable=True)
    duration_ms = Column(Float, default=0.0)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(Text, nullable=True)
    response_body = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="api_logs")


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    test_id = Column(String(50), nullable=True)
    file_path = Column(String(500), nullable=False)
    shot_type = Column(String(30), default="FAILURE")  # STEP, FAILURE, FULLPAGE, EXPLORATORY
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="screenshots")


class BrowserSession(Base):
    __tablename__ = "browser_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    browser_type = Column(String(30), default="chromium")
    session_cookies = Column(JSON, nullable=True)
    local_storage = Column(JSON, nullable=True)
    session_storage = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    test_run = relationship("TestRun", back_populates="browser_sessions")
