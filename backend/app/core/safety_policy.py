import re
from typing import Tuple

SAFE_ACTIONS = {
    "navigate",
    "goto",
    "click",
    "fill",
    "type",
    "select",
    "search",
    "view",
    "login",
    "filter",
    "open",
    "read",
    "check",
    "uncheck",
    "hover",
    "scroll",
    "wait",
    "assert",
    "verify",
}

RESTRICTED_KEYWORDS = [
    r"\bdelete\b",
    r"\bremove\b",
    r"\bdrop\b",
    r"\bpurge\b",
    r"\bpay(ment)?\b",
    r"\bpurchase\b",
    r"\bcheckout\b",
    r"\bsend\s+(email|sms|notification)\b",
    r"\btransfer\b",
    r"\bterminate\b",
    r"\breset\s+password\b",
    r"\bchange\s+(settings|role|permission)\b",
    r"\bclear\s+all\b",
]

RESTRICTED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in RESTRICTED_KEYWORDS]


def is_action_allowed(
    action_type: str,
    target_description: str = "",
    environment: str = "qa",
    is_safe_mode: bool = False
) -> Tuple[bool, str]:
    """
    Evaluates whether an action is safe to execute automatically or requires human intervention.
    In Production or Safe Mode, restricted actions require explicit approval.
    """
    action_lower = action_type.lower()
    target_lower = target_description.lower()
    combined_desc = f"{action_lower} {target_lower}"

    # Check if target matches restricted keywords
    is_restricted = any(p.search(combined_desc) for p in RESTRICTED_PATTERNS)

    if (environment.lower() == "production" or is_safe_mode) and is_restricted:
        return False, f"Action '{action_type}' on '{target_description}' is restricted in {environment.upper()} mode. Human approval required."

    if action_lower not in SAFE_ACTIONS and is_restricted:
        return False, f"Potentially destructive action '{action_type}' requires explicit authorization."

    return True, "Action is authorized."
