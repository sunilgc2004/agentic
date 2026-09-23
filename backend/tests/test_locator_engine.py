import pytest
from app.browser.locator_engine import SmartLocatorEngine


def test_build_priority_selectors():
    selectors = SmartLocatorEngine.build_priority_selectors(
        target_description="Submit Case button",
        hint_selector="#btn-submit-case",
        role="button",
        text="Submit Case"
    )
    
    # Verify priority ordering
    strategies = [s[0] for s in selectors]
    assert "hint" in strategies
    assert "data-testid" in strategies
    assert "role" in strategies
    assert "aria-label" in strategies
    assert "visible-text" in strategies

    # Hint selector should be first
    assert selectors[0] == ("hint", "#btn-submit-case")
