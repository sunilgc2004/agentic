import os
import json
import base64
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import Page, Response, Request
from app.core.config import settings
from app.core.security import mask_sensitive_text, mask_dict
from app.core.logging import logger


class EvidenceCollector:
    """Collects screenshots, DOM snapshots, console logs, and network telemetry."""

    def __init__(self, run_id: str, test_id: Optional[str] = None):
        self.run_id = run_id
        self.test_id = test_id or "global"
        self.run_dir = settings.EVIDENCE_DIR / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.console_logs: List[Dict[str, Any]] = []
        self.network_logs: List[Dict[str, Any]] = []
        self.request_timings: Dict[str, float] = {}

    def attach_listeners(self, page: Page):
        """Attaches console and network listeners to the Playwright page."""

        def on_console(msg):
            entry = {
                "timestamp": time.time(),
                "type": msg.type,
                "text": mask_sensitive_text(msg.text),
                "location": msg.location
            }
            self.console_logs.append(entry)

        def on_request(request: Request):
            self.request_timings[request.url] = time.time()

        def on_response(response: Response):
            start = self.request_timings.pop(response.url, time.time())
            duration_ms = (time.time() - start) * 1000
            
            entry = {
                "timestamp": time.time(),
                "url": mask_sensitive_text(response.url),
                "method": response.request.method,
                "status": response.status,
                "duration_ms": round(duration_ms, 2),
                "headers": mask_dict(dict(response.headers)),
                "is_error": response.status >= 400
            }
            self.network_logs.append(entry)

        def on_request_failed(request: Request):
            start = self.request_timings.pop(request.url, time.time())
            duration_ms = (time.time() - start) * 1000
            
            entry = {
                "timestamp": time.time(),
                "url": mask_sensitive_text(request.url),
                "method": request.method,
                "status": 0,
                "duration_ms": round(duration_ms, 2),
                "error": request.failure,
                "is_error": True
            }
            self.network_logs.append(entry)

        page.on("console", on_console)
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)

    async def capture_screenshot(
        self,
        page: Page,
        step_name: str = "failure",
        full_page: bool = False
    ) -> str:
        """Captures and stores a PNG screenshot, returning the relative/absolute path."""
        safe_step = "".join(c for c in step_name if c.isalnum() or c in ("-", "_"))
        filename = f"{self.test_id}_{safe_step}_{int(time.time() * 1000)}.png"
        filepath = self.run_dir / filename

        try:
            await page.screenshot(path=str(filepath), full_page=full_page)
            logger.info(f"Captured screenshot: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return ""

    async def capture_dom_snapshot(self, page: Page, step_name: str = "failure") -> str:
        """Captures the current DOM HTML."""
        safe_step = "".join(c for c in step_name if c.isalnum() or c in ("-", "_"))
        filename = f"{self.test_id}_{safe_step}_{int(time.time() * 1000)}.html"
        filepath = self.run_dir / filename

        try:
            content = await page.content()
            clean_content = mask_sensitive_text(content)
            filepath.write_text(clean_content, encoding="utf-8")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to capture DOM snapshot: {e}")
            return ""

    def get_console_errors(self) -> List[Dict[str, Any]]:
        return [log for log in self.console_logs if log["type"] in ("error", "warning")]

    def get_network_errors(self) -> List[Dict[str, Any]]:
        return [log for log in self.network_logs if log.get("is_error")]

    def get_summary_evidence(self) -> Dict[str, Any]:
        return {
            "console_errors": self.get_console_errors(),
            "network_errors": self.get_network_errors(),
            "total_requests": len(self.network_logs),
            "recent_console_logs": self.console_logs[-15:]
        }
