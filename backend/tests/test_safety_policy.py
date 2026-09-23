import pytest
from app.core.security import mask_sensitive_text, mask_dict, is_sensitive_key
from app.core.safety_policy import is_action_allowed


def test_credential_masking():
    secret_pass = "MySecretPassword123!"
    log_text = f"User entered password '{secret_pass}' on login form."
    masked = mask_sensitive_text(log_text, custom_secrets=[secret_pass])
    assert secret_pass not in masked
    assert "***MASKED***" in masked


def test_dict_masking():
    data = {
        "username": "tester@example.com",
        "password": "SuperSecretPassword!",
        "api_key": "sk-1234567890",
        "nested": {
            "token": "bearer-jwt-token-999",
            "normal_field": "visible_value"
        }
    }
    cleaned = mask_dict(data)
    assert cleaned["password"] == "***MASKED***"
    assert cleaned["api_key"] == "***MASKED***"
    assert cleaned["nested"]["token"] == "***MASKED***"
    assert cleaned["nested"]["normal_field"] == "visible_value"


def test_safety_policy_safe_actions():
    allowed, reason = is_action_allowed("click", "Dashboard Navigation Link", environment="qa")
    assert allowed is True

    allowed, reason = is_action_allowed("fill", "Search input box", environment="production")
    assert allowed is True


def test_safety_policy_restricted_actions():
    # In production, destructive actions must be blocked
    allowed, reason = is_action_allowed("click", "Delete User Account", environment="production")
    assert allowed is False
    assert "restricted in PRODUCTION" in reason

    allowed, reason = is_action_allowed("click", "Purge database records", environment="qa", is_safe_mode=True)
    assert allowed is False
