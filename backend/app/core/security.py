import re
from typing import Any, Dict, List, Union

SENSITIVE_KEY_PATTERNS = [
    re.compile(r"pass(word)?", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"auth(orization)?", re.IGNORECASE),
    re.compile(r"api[-_]?key", re.IGNORECASE),
    re.compile(r"credit[-_]?card", re.IGNORECASE),
    re.compile(r"cvv", re.IGNORECASE),
    re.compile(r"ssn", re.IGNORECASE),
    re.compile(r"bearer", re.IGNORECASE),
]

MASKED_VALUE = "***MASKED***"


def is_sensitive_key(key: str) -> bool:
    """Check if a dictionary key or field name matches sensitive patterns."""
    return any(pattern.search(key) for pattern in SENSITIVE_KEY_PATTERNS)


def mask_sensitive_text(text: str, custom_secrets: List[str] = None) -> str:
    """Mask known sensitive strings or tokens in text logs/prompts/reports."""
    if not text:
        return text
    
    masked = text
    
    # Mask any custom secrets passed in (e.g. current user password or API key)
    if custom_secrets:
        for secret in custom_secrets:
            if secret and len(secret) >= 3:
                masked = masked.replace(secret, MASKED_VALUE)
    
    # Mask common JWT / Bearer patterns
    masked = re.sub(r"(Bearer\s+)[A-Za-z0-9\-_.]+", r"\1" + MASKED_VALUE, masked, flags=re.IGNORECASE)
    # Mask key-value secrets in query strings or JSON-like text
    masked = re.sub(
        r'("(?:password|token|secret|apiKey|api_key|auth)"\s*:\s*)"[^"]*"',
        r'\1"***MASKED***"',
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"((?:password|token|secret|apiKey|api_key|auth)=)[^&\s]+",
        r"\1***MASKED***",
        masked,
        flags=re.IGNORECASE
    )
    return masked


def mask_dict(data: Union[Dict, List, Any], custom_secrets: List[str] = None) -> Union[Dict, List, Any]:
    """Recursively mask sensitive values in nested dictionaries and lists."""
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if is_sensitive_key(str(k)):
                result[k] = MASKED_VALUE
            elif isinstance(v, (dict, list)):
                result[k] = mask_dict(v, custom_secrets)
            elif isinstance(v, str):
                result[k] = mask_sensitive_text(v, custom_secrets)
            else:
                result[k] = v
        return result
    elif isinstance(data, list):
        return [mask_dict(item, custom_secrets) for item in data]
    elif isinstance(data, str):
        return mask_sensitive_text(data, custom_secrets)
    return data
