import json
from typing import List, Dict, Any, Optional
from app.schemas.agent_schemas import PageMapSchema, GeneratedTestCase, TestStep
from app.services.test_data_generator import TestDataGenerator
from app.agents.llm_provider import get_llm_provider
from app.core.logging import logger


class TestCaseGeneratorAgent:
    """Agent 2: Generates comprehensive test cases based on page map, test mode, or natural language prompts."""

    @classmethod
    async def generate_suite(
        cls,
        page_map: PageMapSchema,
        test_mode: str = "SMOKE",
        credentials: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None
    ) -> List[GeneratedTestCase]:
        mode = test_mode.upper()
        logger.info(f"Agent 2 (Test Generator): Generating test suite for mode={mode}...")

        if custom_prompt:
            return [await cls.generate_from_natural_language(page_map, custom_prompt)]

        generated_cases: List[GeneratedTestCase] = []

        if mode in ("SMOKE", "FULL_QA"):
            generated_cases.extend(cls._generate_smoke_tests(page_map, credentials))

        if mode in ("FUNCTIONAL", "FULL_QA"):
            generated_cases.extend(cls._generate_functional_tests(page_map))

        if mode in ("NEGATIVE", "FULL_QA"):
            generated_cases.extend(cls._generate_negative_tests(page_map))

        if mode in ("UI", "FULL_QA"):
            generated_cases.extend(cls._generate_ui_tests(page_map))

        if not generated_cases:
            # Fallback to standard functional case
            generated_cases.extend(cls._generate_smoke_tests(page_map, credentials))

        logger.info(f"Agent 2 (Test Generator): Successfully generated {len(generated_cases)} test cases.")
        return generated_cases

    @classmethod
    def _generate_smoke_tests(
        cls,
        page_map: PageMapSchema,
        credentials: Optional[Dict[str, Any]] = None
    ) -> List[GeneratedTestCase]:
        cases = []
        user = credentials.get("username", "test@example.com") if credentials else "test@example.com"
        pwd = credentials.get("password", "SecurePass123!") if credentials else "SecurePass123!"

        # 1. App Launch & Login
        cases.append(GeneratedTestCase(
            custom_id="TC_SMOKE_001",
            module="Authentication",
            feature="Login",
            scenario="Verify application launch and successful login with valid credentials.",
            preconditions="User account exists and application is accessible.",
            test_data={"username": user, "password": pwd},
            steps=[
                TestStep(step_number=1, action="navigate", target_description="Application Base URL", value=page_map.url),
                TestStep(step_number=2, action="fill", target_description="Username field", selector="#username, input[name='username'], [placeholder*='email' i]", value=user),
                TestStep(step_number=3, action="fill", target_description="Password field", selector="#password, input[name='password'], [type='password']", value=pwd),
                TestStep(step_number=4, action="click", target_description="Login button", selector="#btn-login, button[type='submit']"),
                TestStep(step_number=5, action="assert_visible", target_description="Dashboard navigation header", selector="nav, #dashboard-header, text='Dashboard'")
            ],
            expected_result="User should successfully authenticate and arrive at the dashboard.",
            priority="Critical",
            test_type="Smoke"
        ))

        # 2. Case Management - Create Operation
        synthetic = TestDataGenerator.generate_dataset()
        cases.append(GeneratedTestCase(
            custom_id="TC_SMOKE_002",
            module="Case Management",
            feature="Create Case",
            scenario="Verify creation of a new arbitration case with valid claimant and respondent.",
            preconditions="User is authenticated.",
            test_data=synthetic,
            steps=[
                TestStep(step_number=1, action="click", target_description="Case Management link", selector="a:has-text('Case Management'), #nav-cases"),
                TestStep(step_number=2, action="click", target_description="Create Case button", selector="#btn-create-case, button:has-text('Create Case')"),
                TestStep(step_number=3, action="fill", target_description="Claimant field", selector="#claimant_name, input[name='claimant_name']", value=synthetic["claimant_name"]),
                TestStep(step_number=4, action="fill", target_description="Respondent field", selector="#respondent_name, input[name='respondent_name']", value=synthetic["respondent_name"]),
                TestStep(step_number=5, action="fill", target_description="Dispute Amount field", selector="#dispute_amount, input[name='dispute_amount']", value=synthetic["dispute_amount"]),
                TestStep(step_number=6, action="click", target_description="Submit Case button", selector="#btn-submit-case, button[type='submit']"),
                TestStep(step_number=7, action="assert_visible", target_description="Case Success Alert", selector=".alert-success, #case-created-banner, text='Case Created'")
            ],
            expected_result="Case record should be created and visible in the active case list.",
            priority="High",
            test_type="Smoke"
        ))

        # 3. Case Action - Generate VC Link
        cases.append(GeneratedTestCase(
            custom_id="TC_SMOKE_003",
            module="Case Management",
            feature="Generate VC Link",
            scenario="Verify generating a video conference link for an active arbitration case.",
            preconditions="At least one case exists.",
            test_data={"case_id": "ARB-CURRENT"},
            steps=[
                TestStep(step_number=1, action="click", target_description="Active Case Row Action", selector="#btn-open-case, table tr:first-child a"),
                TestStep(step_number=2, action="click", target_description="Generate VC Link button", selector="#btn-generate-vc, button:has-text('Generate VC')"),
                TestStep(step_number=3, action="assert_visible", target_description="Video Conference Link Badge", selector="#vc-link-url, .vc-conference-url, text='https://meet.'")
            ],
            expected_result="A valid video conference link should be generated and displayed.",
            priority="High",
            test_type="Smoke"
        ))

        # 4. Logout Workflow
        cases.append(GeneratedTestCase(
            custom_id="TC_SMOKE_004",
            module="Authentication",
            feature="Logout",
            scenario="Verify user can terminate session and logout successfully.",
            preconditions="User is logged in.",
            test_data=None,
            steps=[
                TestStep(step_number=1, action="click", target_description="Logout button", selector="#btn-logout, a:has-text('Logout'), button:has-text('Logout')"),
                TestStep(step_number=2, action="assert_visible", target_description="Login Form", selector="input[name='username'], #username, button[type='submit']")
            ],
            expected_result="User session ends and user is redirected to login screen.",
            priority="Medium",
            test_type="Smoke"
        ))

        return cases

    @classmethod
    def _generate_negative_tests(cls, page_map: PageMapSchema) -> List[GeneratedTestCase]:
        cases = []
        neg_data = TestDataGenerator.get_negative_payloads()

        # 1. Negative Auth: Invalid credentials
        cases.append(GeneratedTestCase(
            custom_id="TC_NEG_001",
            module="Authentication",
            feature="Login Validation",
            scenario="Attempt login with invalid credentials and check for proper error rejection.",
            preconditions="User is on login page.",
            test_data={"username": "unregistered@domain.com", "password": "WrongPassword999!"},
            steps=[
                TestStep(step_number=1, action="navigate", target_description="Base URL", value=page_map.url),
                TestStep(step_number=2, action="fill", target_description="Username field", selector="#username, input[name='username']", value="unregistered@domain.com"),
                TestStep(step_number=3, action="fill", target_description="Password field", selector="#password, input[name='password']", value="WrongPassword999!"),
                TestStep(step_number=4, action="click", target_description="Login button", selector="#btn-login, button[type='submit']"),
                TestStep(step_number=5, action="assert_visible", target_description="Error alert", selector=".alert-danger, #login-error, text='Invalid credentials'")
            ],
            expected_result="System should reject invalid authentication and display clear error message.",
            priority="High",
            test_type="Negative"
        ))

        # 2. Negative Form: SQL Injection Input in Search
        cases.append(GeneratedTestCase(
            custom_id="TC_NEG_002",
            module="Case Management",
            feature="Input Sanitization",
            scenario="Submit SQL-like input into search field to verify SQL injection resilience.",
            preconditions="User is on case search page.",
            test_data={"payload": neg_data["sql_injection_payloads"][0]},
            steps=[
                TestStep(step_number=1, action="fill", target_description="Search box", selector="#search-input, input[type='search'], [placeholder*='Search']", value="' OR '1'='1"),
                TestStep(step_number=2, action="click", target_description="Search button", selector="#btn-search, button:has-text('Search')"),
                TestStep(step_number=3, action="assert_visible", target_description="Safe Search Result or Empty State", selector="#no-results, .results-container")
            ],
            expected_result="Application safely handles SQL characters without 500 error or syntax leak.",
            priority="High",
            test_type="Negative"
        ))

        # 3. Negative Form: Required Field Empty on Case Creation
        cases.append(GeneratedTestCase(
            custom_id="TC_NEG_003",
            module="Case Management",
            feature="Form Validation",
            scenario="Submit new case form with empty claimant and negative dispute amount.",
            preconditions="User opens case creation modal.",
            test_data={"claimant": "", "respondent": "ACME Corp", "amount": "-500"},
            steps=[
                TestStep(step_number=1, action="click", target_description="Create Case button", selector="#btn-create-case, button:has-text('Create Case')"),
                TestStep(step_number=2, action="fill", target_description="Claimant field", selector="#claimant_name, input[name='claimant_name']", value=""),
                TestStep(step_number=3, action="fill", target_description="Respondent field", selector="#respondent_name, input[name='respondent_name']", value="ACME Corp"),
                TestStep(step_number=4, action="fill", target_description="Dispute amount", selector="#dispute_amount, input[name='dispute_amount']", value="-500"),
                TestStep(step_number=5, action="click", target_description="Submit Case button", selector="#btn-submit-case, button[type='submit']"),
                TestStep(step_number=6, action="assert_visible", target_description="Validation error message", selector=".field-error, :invalid, text='required'")
            ],
            expected_result="Client-side or server-side validation error prevents submission of invalid negative values.",
            priority="Medium",
            test_type="Negative"
        ))

        return cases

    @classmethod
    def _generate_functional_tests(cls, page_map: PageMapSchema) -> List[GeneratedTestCase]:
        cases = []
        cases.append(GeneratedTestCase(
            custom_id="TC_FUNC_001",
            module="Navigation",
            feature="Menu Traversal",
            scenario="Verify all primary navigation links load their respective views.",
            preconditions="Application is running.",
            test_data=None,
            steps=[
                TestStep(step_number=1, action="click", target_description="Dashboard link", selector="a:has-text('Dashboard')"),
                TestStep(step_number=2, action="assert_visible", target_description="Dashboard View", selector="#dashboard-view, main"),
                TestStep(step_number=3, action="click", target_description="Cases link", selector="a:has-text('Case Management')"),
                TestStep(step_number=4, action="assert_visible", target_description="Cases Table", selector="table, #cases-table")
            ],
            expected_result="User can smoothly navigate across modules without errors.",
            priority="Medium",
            test_type="Functional"
        ))
        return cases

    @classmethod
    def _generate_ui_tests(cls, page_map: PageMapSchema) -> List[GeneratedTestCase]:
        cases = []
        cases.append(GeneratedTestCase(
            custom_id="TC_UI_001",
            module="UI / Layout",
            feature="Responsive Layout & Visibility",
            scenario="Verify essential UI elements (buttons, tables, navigation) are visible and responsive.",
            preconditions="Page loaded.",
            test_data=None,
            steps=[
                TestStep(step_number=1, action="assert_visible", target_description="Application Header", selector="header, nav"),
                TestStep(step_number=2, action="assert_visible", target_description="Main Content Area", selector="main, .container, #app-root")
            ],
            expected_result="Header and main container render without layout overlap or overflow.",
            priority="Low",
            test_type="UI"
        ))
        return cases

    @classmethod
    async def generate_from_natural_language(
        cls,
        page_map: PageMapSchema,
        prompt: str
    ) -> GeneratedTestCase:
        """Parses natural language user instruction into a structured executable test case."""
        llm = get_llm_provider()
        system_instruction = (
            f"You are Agent 2 (Test Case Generator). Convert this user request into a structured test case JSON.\n"
            f"Request: '{prompt}'\n"
            f"Available page buttons: {[b.text for b in page_map.buttons[:5]]}\n"
            f"Return JSON adhering to GeneratedTestCase schema with custom_id, module, feature, scenario, steps, expected_result, priority."
        )
        try:
            res = await llm.generate_json(system_instruction)
            if "steps" in res and isinstance(res["steps"], list):
                steps = [TestStep(**s) for s in res["steps"]]
                return GeneratedTestCase(
                    custom_id=res.get("custom_id", "TC_NL_001"),
                    module=res.get("module", "General"),
                    feature=res.get("feature", "Custom Flow"),
                    scenario=res.get("scenario", prompt),
                    preconditions=res.get("preconditions"),
                    test_data=res.get("test_data"),
                    steps=steps,
                    expected_result=res.get("expected_result", "Operation completes successfully."),
                    priority=res.get("priority", "Medium"),
                    test_type="Custom"
                )
        except Exception as e:
            logger.error(f"Natural language generation error: {e}")

        # Fallback generated test case
        return GeneratedTestCase(
            custom_id="TC_NL_001",
            module="Arbitration",
            feature="Case Creation Flow",
            scenario=prompt,
            preconditions="User is logged in.",
            test_data={"claimant": "Alex Smith", "respondent": "Jordan Doe"},
            steps=[
                TestStep(step_number=1, action="click", target_description="Create Case button", selector="#btn-create-case, button:has-text('Create')"),
                TestStep(step_number=2, action="fill", target_description="Claimant name", selector="#claimant_name", value="Alex Smith"),
                TestStep(step_number=3, action="fill", target_description="Respondent name", selector="#respondent_name", value="Jordan Doe"),
                TestStep(step_number=4, action="click", target_description="Submit button", selector="#btn-submit-case, button[type='submit']"),
                TestStep(step_number=5, action="assert_visible", target_description="Success notification", selector=".alert-success, text='Created'")
            ],
            expected_result="Arbitration case is created and confirmed via UI notice.",
            priority="High",
            test_type="Custom"
        )
