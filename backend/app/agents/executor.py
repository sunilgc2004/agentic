import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from playwright.async_api import Page
from app.schemas.agent_schemas import GeneratedTestCase, TestStep, StepExecutionResult
from app.browser.locator_engine import SmartLocatorEngine
from app.browser.evidence_collector import EvidenceCollector
from app.core.safety_policy import is_action_allowed
from app.core.logging import logger, StructuredLogger


class BrowserExecutionAgent:
    """Agent 3: Converts abstract test steps into robust Playwright actions with self-healing."""

    def __init__(
        self,
        page: Page,
        evidence_collector: EvidenceCollector,
        run_id: str,
        environment: str = "qa",
        on_step_update: Optional[Callable] = None
    ):
        self.page = page
        self.evidence_collector = evidence_collector
        self.run_id = run_id
        self.environment = environment
        self.on_step_update = on_step_update

    async def execute_test_case(
        self,
        test_case: GeneratedTestCase
    ) -> Tuple[List[StepExecutionResult], Optional[str]]:
        """
        Executes each step of a test case sequentially.
        Returns: (step_results, failure_screenshot_path)
        """
        step_results: List[StepExecutionResult] = []
        failure_screenshot: Optional[str] = None

        logger.info(f"Agent 3 (Executor): Starting execution for {test_case.custom_id} - '{test_case.scenario}'")

        for step in test_case.steps:
            step_start = time.time()
            target_desc = step.target_description or step.selector or "Unknown"

            # 1. Safety verification check
            is_allowed, reason = is_action_allowed(step.action, target_desc, self.environment)
            if not is_allowed:
                logger.warning(f"Action blocked by safety policy: {reason}")
                res = StepExecutionResult(
                    step_number=step.step_number,
                    action=step.action,
                    target=target_desc,
                    status="BLOCKED",
                    duration_ms=(time.time() - step_start) * 1000,
                    error=reason
                )
                step_results.append(res)
                StructuredLogger.log_action(
                    self.run_id, test_case.custom_id, "BrowserExecutor",
                    step.action, target_desc, "BLOCKED", res.duration_ms, error=reason
                )
                break

            # 2. Execute step
            try:
                recovered_sel = None
                if step.action == "navigate":
                    target_url = step.value or target_desc
                    await self.page.goto(target_url, wait_until="load", timeout=30000)

                elif step.action in ("click", "fill", "select", "check", "assert_visible", "assert_text"):
                    locator, used_selector, was_healed = await SmartLocatorEngine.find_element(
                        self.page, target_desc, step.selector
                    )
                    if was_healed:
                        recovered_sel = used_selector

                    if not locator:
                        raise TimeoutError(f"Element '{target_desc}' could not be located using priority selectors or self-healing.")

                    # Perform action
                    if step.action == "click":
                        await locator.click(timeout=10000)
                    elif step.action == "fill":
                        await locator.fill(step.value or "")
                    elif step.action == "select":
                        await locator.select_option(value=step.value)
                    elif step.action == "check":
                        await locator.check()
                    elif step.action == "assert_visible":
                        is_vis = await locator.is_visible()
                        if not is_vis:
                            raise AssertionError(f"Element '{target_desc}' is not visible.")
                    elif step.action == "assert_text":
                        actual_text = await locator.inner_text()
                        if step.value and step.value not in actual_text:
                            raise AssertionError(f"Expected text '{step.value}' not found in '{actual_text}'.")

                elif step.action == "wait":
                    wait_time = float(step.value or "1.0")
                    await self.page.wait_for_timeout(wait_time * 1000)

                # Brief UI stabilization wait
                await self.page.wait_for_timeout(400)

                # Capture step screenshot for real-time live browser preview
                step_screenshot = None
                try:
                    step_screenshot = await self.evidence_collector.capture_screenshot(
                        self.page, step_name=f"step_{step.step_number}"
                    )
                except Exception:
                    step_screenshot = None

                duration_ms = (time.time() - step_start) * 1000
                step_res = StepExecutionResult(
                    step_number=step.step_number,
                    action=step.action,
                    target=target_desc,
                    status="SUCCESS",
                    duration_ms=round(duration_ms, 2),
                    recovered_selector=recovered_sel,
                    screenshot_path=step_screenshot
                )
                step_results.append(step_res)

                StructuredLogger.log_action(
                    self.run_id, test_case.custom_id, "BrowserExecutor",
                    step.action, target_desc, "SUCCESS", duration_ms,
                    metadata={"recovered_selector": recovered_sel} if recovered_sel else None
                )

                if self.on_step_update:
                    await self.on_step_update(step_res)

            except Exception as e:
                duration_ms = (time.time() - step_start) * 1000
                err_msg = str(e)
                logger.error(f"Step {step.step_number} failed ({step.action} on {target_desc}): {err_msg}")

                # Capture rich failure evidence
                failure_screenshot = await self.evidence_collector.capture_screenshot(
                    self.page, step_name=f"step_{step.step_number}_fail"
                )
                await self.evidence_collector.capture_dom_snapshot(
                    self.page, step_name=f"step_{step.step_number}_fail"
                )

                step_res = StepExecutionResult(
                    step_number=step.step_number,
                    action=step.action,
                    target=target_desc,
                    status="FAILED",
                    duration_ms=round(duration_ms, 2),
                    error=err_msg,
                    screenshot_path=failure_screenshot
                )
                step_results.append(step_res)

                StructuredLogger.log_action(
                    self.run_id, test_case.custom_id, "BrowserExecutor",
                    step.action, target_desc, "FAILED", duration_ms, error=err_msg
                )

                if self.on_step_update:
                    await self.on_step_update(step_res)

                # Stop this test case upon step failure, preserve browser for subsequent independent tests
                break

        return step_results, failure_screenshot
