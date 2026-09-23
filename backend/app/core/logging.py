import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.security import mask_dict, mask_sensitive_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("ai_qa_agent")


class StructuredLogger:
    """Structured QA execution logger adhering to Section 37 requirements."""
    
    @staticmethod
    def log_action(
        run_id: str,
        test_id: Optional[str],
        agent: str,
        action: str,
        target: str,
        result: str,
        duration_ms: float = 0.0,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        
        # Ensure credentials / sensitive data are masked in logs
        clean_target = mask_sensitive_text(target)
        clean_error = mask_sensitive_text(error) if error else None
        clean_meta = mask_dict(metadata or {})
        
        log_entry = {
            "timestamp": timestamp,
            "run_id": run_id,
            "test_id": test_id,
            "agent": agent,
            "action": action,
            "target": clean_target,
            "result": result,
            "duration_ms": round(duration_ms, 2),
            "error": clean_error,
            "metadata": clean_meta,
        }
        
        log_str = (
            f"[{timestamp}] RUN:{run_id} TEST:{test_id or 'GLOBAL'} AGENT:{agent} "
            f"ACTION:{action} TARGET:{clean_target} RESULT:{result} ({round(duration_ms, 2)}ms)"
        )
        if error:
            log_str += f" ERROR:{clean_error}"
            logger.error(log_str)
        else:
            logger.info(log_str)
            
        return log_entry
