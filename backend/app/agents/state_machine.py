from enum import Enum
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class AgentState(str, Enum):
    IDLE = "IDLE"
    DISCOVER = "DISCOVER"
    PLAN = "PLAN"
    VALIDATE_PLAN = "VALIDATE_PLAN"
    EXECUTE = "EXECUTE"
    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    RECOVER = "RECOVER"
    RETRY = "RETRY"
    VERIFY = "VERIFY"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    REPORT = "REPORT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentStateMachine:
    """Manages explicit state transitions, loop safety, and max retry limits."""

    def __init__(self, max_retries: int = None):
        self.current_state = AgentState.IDLE
        self.max_retries = max_retries or settings.MAX_RETRIES
        self.retry_count = 0
        self.state_history = []

    def transition_to(self, new_state: AgentState, reason: str = ""):
        logger.info(f"StateMachine: {self.current_state.value} -> {new_state.value} ({reason})")
        self.state_history.append({"from": self.current_state.value, "to": new_state.value, "reason": reason})
        self.current_state = new_state

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    def record_retry(self):
        self.retry_count += 1
        logger.info(f"StateMachine: Retry recorded ({self.retry_count}/{self.max_retries})")

    def reset_retry(self):
        self.retry_count = 0
