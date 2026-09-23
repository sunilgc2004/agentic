import json
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from app.core.config import settings
from app.core.logging import logger


class BrowserManager:
    """Manages Playwright browser lifecycle, context, sessions, and multi-browser support."""

    def __init__(self, browser_type: str = "chromium", headless: bool = True):
        self.browser_type_name = browser_type.lower()
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def initialize(self, storage_state: Optional[Dict[str, Any]] = None) -> Page:
        self.playwright = await async_playwright().start()

        browser_map = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }
        launcher = browser_map.get(self.browser_type_name, self.playwright.chromium)

        logger.info(f"Launching {self.browser_type_name} (headless={self.headless})...")
        self.browser = await launcher.launch(
            headless=self.headless,
            args=["--disable-dev-shm-usage", "--no-sandbox"] if self.browser_type_name == "chromium" else []
        )

        context_options = {
            "viewport": {"width": 1280, "height": 800},
            "ignore_https_errors": True,
        }
        if storage_state:
            context_options["storage_state"] = storage_state

        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        self.page.set_default_timeout(settings.BROWSER_TIMEOUT_MS)
        return self.page

    async def get_storage_state(self) -> Dict[str, Any]:
        if self.context:
            return await self.context.storage_state()
        return {}

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser session closed cleanly.")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
