import json
from typing import Dict, Any, Optional
from playwright.async_api import Page
from app.schemas.agent_schemas import PageMapSchema, PageElementInfo, PageFormInfo
from app.agents.llm_provider import get_llm_provider
from app.core.logging import logger


class ApplicationExplorerAgent:
    """Agent 1: Explores the application DOM, discovers routes, buttons, forms, workflows."""

    DISCOVERY_JS = """
    () => {
        const getAttr = (el, attr) => el.getAttribute(attr) || null;
        
        // 1. Navigation links
        const navLinks = Array.from(document.querySelectorAll('nav a, header a, a[href]'))
            .filter(a => a.href && !a.href.startsWith('javascript:') && a.offsetParent !== null)
            .map(a => ({
                tag: 'a',
                role: 'link',
                text: (a.innerText || a.textContent || '').trim().substring(0, 50),
                aria_label: getAttr(a, 'aria-label'),
                data_testid: getAttr(a, 'data-testid'),
                selector: a.id ? '#' + a.id : `a[href="${getAttr(a, 'href')}"]`,
                href: getAttr(a, 'href'),
                is_interactive: true
            }));

        // 2. Buttons
        const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"], [role="button"]'))
            .filter(b => b.offsetParent !== null)
            .map(b => ({
                tag: b.tagName.toLowerCase(),
                role: 'button',
                text: (b.innerText || b.value || b.textContent || '').trim().substring(0, 50),
                aria_label: getAttr(b, 'aria-label'),
                data_testid: getAttr(b, 'data-testid'),
                name: getAttr(b, 'name'),
                selector: b.id ? '#' + b.id : (getAttr(b, 'data-testid') ? `[data-testid="${getAttr(b, 'data-testid')}"]` : null),
                is_interactive: !b.disabled
            }));

        // 3. Forms and inputs
        const forms = Array.from(document.querySelectorAll('form')).map(f => {
            const inputs = Array.from(f.querySelectorAll('input, select, textarea')).map(input => ({
                tag: input.tagName.toLowerCase(),
                name: getAttr(input, 'name'),
                input_type: getAttr(input, 'type') || 'text',
                placeholder: getAttr(input, 'placeholder'),
                aria_label: getAttr(input, 'aria-label'),
                data_testid: getAttr(input, 'data-testid'),
                selector: input.id ? '#' + input.id : (getAttr(input, 'name') ? `[name="${getAttr(input, 'name')}"]` : null),
                is_interactive: !input.disabled
            }));
            const submitBtn = f.querySelector('button[type="submit"], input[type="submit"], button');
            return {
                form_id: f.id || null,
                action: getAttr(f, 'action'),
                method: getAttr(f, 'method') || 'POST',
                fields: inputs,
                submit_button: submitBtn ? {
                    tag: submitBtn.tagName.toLowerCase(),
                    text: (submitBtn.innerText || submitBtn.value || '').trim(),
                    selector: submitBtn.id ? '#' + submitBtn.id : null
                } : null
            };
        });

        // 4. Tables and Modals
        const tables = Array.from(document.querySelectorAll('table')).map(t => ({
            id: t.id || null,
            headers: Array.from(t.querySelectorAll('th')).map(th => (th.innerText || '').trim()),
            rowCount: t.querySelectorAll('tbody tr').length
        }));

        const modals = Array.from(document.querySelectorAll('[role="dialog"], .modal, dialog')).map(m => ({
            id: m.id || null,
            title: (m.querySelector('h1, h2, h3, .modal-title')?.innerText || '').trim()
        }));

        return {
            title: document.title,
            url: window.location.href,
            navigation_links: navLinks.slice(0, 30),
            buttons: buttons.slice(0, 30),
            forms: forms.slice(0, 10),
            tables: tables.slice(0, 10),
            modals: modals.slice(0, 5)
        };
    }
    """

    @classmethod
    async def explore_page(cls, page: Page, base_url: str) -> PageMapSchema:
        """Navigates, scans DOM, and uses LLM/Heuristic to infer workflows and map."""
        try:
            await page.goto(base_url, wait_until="load", timeout=30000)
            await page.wait_for_timeout(1500)
        except Exception as e:
            logger.warning(f"Navigation with load timed out ({e}), retrying with domcontentloaded...")
            await page.goto(base_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(1500)

        raw_data = await page.evaluate(cls.DISCOVERY_JS)

        # Build prompt for LLM structuring
        prompt = (
            f"You are Agent 1 (Application Explorer). Analyze the discovered DOM information:\n"
            f"Title: {raw_data.get('title')}\n"
            f"URL: {raw_data.get('url')}\n"
            f"Discovered Buttons: {json.dumps(raw_data.get('buttons', [])[:10])}\n"
            f"Discovered Forms: {json.dumps(raw_data.get('forms', [])[:5])}\n"
            f"Discovered Links: {json.dumps(raw_data.get('navigation_links', [])[:10])}\n"
            f"Task: Identify high-level business workflows (e.g. Login, CRUD, Verification) "
            f"and return a PageMapSchema JSON."
        )

        llm = get_llm_provider()
        llm_response = await llm.generate_json(prompt)

        # Merge raw extraction with LLM reasoning
        workflows = llm_response.get("discovered_workflows", [
            "Application Launch",
            "Authentication",
            "Dashboard Navigation",
            "Record Creation",
            "Form Submission"
        ])

        routes = list(set([base_url] + [link.get("href") for link in raw_data.get("navigation_links", []) if link.get("href")]))

        page_map = PageMapSchema(
            url=raw_data.get("url", base_url),
            title=raw_data.get("title", "Application"),
            routes=routes[:15],
            navigation_links=[PageElementInfo(**item) for item in raw_data.get("navigation_links", [])],
            interactive_elements=[],
            forms=[PageFormInfo(**f) for f in raw_data.get("forms", [])],
            buttons=[PageElementInfo(**b) for b in raw_data.get("buttons", [])],
            tables=raw_data.get("tables", []),
            modals=raw_data.get("modals", []),
            discovered_workflows=workflows
        )
        logger.info(f"Agent 1 (Explorer): Explored {page_map.url} with {len(page_map.buttons)} buttons and {len(workflows)} workflows.")
        return page_map
