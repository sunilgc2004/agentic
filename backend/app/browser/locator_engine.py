import re
from typing import Optional, Dict, Any, Tuple
from playwright.async_api import Page, Locator
from app.core.logging import logger


class SmartLocatorEngine:
    """
    Intelligent element locator with priority hierarchy and self-healing recovery.
    Priority:
    1. data-testid
    2. accessibility role + name
    3. aria-label
    4. label
    5. name
    6. placeholder
    7. visible text
    8. CSS selector
    9. XPath
    """

    @staticmethod
    def build_priority_selectors(
        target_description: str,
        hint_selector: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None,
        placeholder: Optional[str] = None,
        name: Optional[str] = None
    ) -> list:
        selectors = []

        # 1. Direct hint if provided
        if hint_selector:
            selectors.append(("hint", hint_selector))

        clean_text = (text or target_description).strip()
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", clean_text.lower())

        # 2. data-testid
        selectors.append(("data-testid", f'[data-testid="{slug}"]'))
        selectors.append(("data-testid-exact", f'[data-testid="{clean_text}"]'))
        selectors.append(("data-test", f'[data-test="{slug}"]'))

        # 3. Accessibility role & name
        if role:
            selectors.append(("role", f"role={role}[name='{clean_text}']"))

        # 4. aria-label
        selectors.append(("aria-label", f'[aria-label="{clean_text}" i]'))
        selectors.append(("aria-label-contains", f'[aria-label*="{clean_text}" i]'))

        # 5. Label
        selectors.append(("label", f'label:has-text("{clean_text}")'))

        # 6. Name
        if name:
            selectors.append(("name", f'[name="{name}"]'))
        selectors.append(("name-guess", f'[name="{slug}"]'))

        # 7. Placeholder
        if placeholder:
            selectors.append(("placeholder", f'[placeholder="{placeholder}" i]'))
        selectors.append(("placeholder-guess", f'[placeholder="{clean_text}" i]'))

        # 8. Visible text
        selectors.append(("visible-text", f'text="{clean_text}"'))
        selectors.append(("button-text", f'button:has-text("{clean_text}")'))
        selectors.append(("link-text", f'a:has-text("{clean_text}")'))

        # 9. Generic ID / class fallback if clean_text resembles an ID
        if not re.search(r"\s", clean_text):
            selectors.append(("id", f"#{clean_text}"))
            selectors.append(("id-lower", f"#{slug}"))

        return selectors

    @classmethod
    async def find_element(
        cls,
        page: Page,
        target_description: str,
        hint_selector: Optional[str] = None,
        timeout_ms: int = 5000
    ) -> Tuple[Optional[Locator], str, bool]:
        """
        Attempts to locate an element using the priority hierarchy.
        If initial attempts fail, triggers self-healing DOM inspection.
        Returns: (Locator, selector_used, was_self_healed)
        """
        priority_list = cls.build_priority_selectors(target_description, hint_selector)

        for strategy, selector in priority_list:
            try:
                locator = page.locator(selector).first
                if await locator.count() > 0 and await locator.is_visible():
                    return locator, selector, False
            except Exception:
                continue

        # Initial strategies failed. Trigger Self-Healing Recovery
        logger.warning(f"Initial locators failed for '{target_description}'. Initiating Self-Healing recovery...")
        recovered_locator, recovered_selector = await cls.self_heal_locator(page, target_description)

        if recovered_locator:
            logger.info(f"SELF-HEALED: Successfully recovered locator for '{target_description}' -> '{recovered_selector}'")
            return recovered_locator, recovered_selector, True

        return None, hint_selector or target_description, False

    @classmethod
    async def self_heal_locator(cls, page: Page, target_description: str) -> Tuple[Optional[Locator], Optional[str]]:
        """
        Self-healing engine: Inspects DOM for semantic, contextual, and nearby text equivalence.
        Verifies visibility and interactive attributes before returning.
        """
        keywords = [k.lower() for k in re.findall(r"\w+", target_description) if len(k) > 2]
        if not keywords:
            return None, None

        # DOM inspection script
        js_code = """
        (keywords) => {
            const candidates = [];
            const elements = document.querySelectorAll('button, a, input, select, textarea, [role="button"], [role="link"], [role="menuitem"], [role="tab"]');
            
            for (const el of elements) {
                const text = (el.innerText || el.textContent || '').toLowerCase();
                const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                const placeholder = (el.getAttribute('placeholder') || '').toLowerCase();
                const name = (el.getAttribute('name') || '').toLowerCase();
                const id = (el.id || '').toLowerCase();
                const role = (el.getAttribute('role') || el.tagName).toLowerCase();
                
                let score = 0;
                for (const kw of keywords) {
                    if (text.includes(kw)) score += 3;
                    if (aria.includes(kw)) score += 3;
                    if (placeholder.includes(kw)) score += 2;
                    if (name.includes(kw)) score += 2;
                    if (id.includes(kw)) score += 2;
                }
                
                // Verify visibility and not disabled
                const rect = el.getBoundingClientRect();
                const isVisible = rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden';
                const isEnabled = !el.disabled && el.getAttribute('aria-disabled') !== 'true';
                
                if (score > 0 && isVisible && isEnabled) {
                    // Generate robust unique selector
                    let sel = '';
                    if (el.id) {
                        sel = '#' + el.id;
                    } else if (el.getAttribute('data-testid')) {
                        sel = `[data-testid="${el.getAttribute('data-testid')}"]`;
                    } else if (el.getAttribute('aria-label')) {
                        sel = `${el.tagName.toLowerCase()}[aria-label="${el.getAttribute('aria-label')}"]`;
                    } else if (text.trim().length > 0 && text.trim().length < 40) {
                        sel = `${el.tagName.toLowerCase()}:has-text("${text.trim()}")`;
                    } else {
                        sel = el.tagName.toLowerCase();
                    }
                    candidates.push({ selector: sel, score: score, tagName: el.tagName });
                }
            }
            candidates.sort((a, b) => b.score - a.score);
            return candidates.length > 0 ? candidates[0].selector : null;
        }
        """
        try:
            suggested_selector = await page.evaluate(js_code, keywords)
            if suggested_selector:
                locator = page.locator(suggested_selector).first
                if await locator.count() > 0 and await locator.is_visible():
                    return locator, suggested_selector
        except Exception as e:
            logger.error(f"Self-healing DOM evaluation failed: {e}")

        return None, None
