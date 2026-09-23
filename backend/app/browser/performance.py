import time
from typing import Dict, Any, List


class PerformanceMonitor:
    """Tracks page navigation durations, API response latencies, and flags slow operations."""

    SLOW_PAGE_LOAD_THRESHOLD_MS = 5000.0
    SLOW_API_THRESHOLD_MS = 2000.0

    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []

    def record_metric(self, metric_type: str, name: str, duration_ms: float, metadata: Dict[str, Any] = None):
        is_slow = False
        if metric_type == "page_load" and duration_ms > self.SLOW_PAGE_LOAD_THRESHOLD_MS:
            is_slow = True
        elif metric_type == "api_request" and duration_ms > self.SLOW_API_THRESHOLD_MS:
            is_slow = True

        self.metrics.append({
            "timestamp": time.time(),
            "type": metric_type,
            "name": name,
            "duration_ms": round(duration_ms, 2),
            "is_slow": is_slow,
            "metadata": metadata or {}
        })

    def get_slow_operations(self) -> List[Dict[str, Any]]:
        return [m for m in self.metrics if m["is_slow"]]

    def get_summary(self) -> Dict[str, Any]:
        durations = [m["duration_ms"] for m in self.metrics]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        return {
            "total_operations": len(self.metrics),
            "avg_duration_ms": round(avg_duration, 2),
            "slow_operations_count": len(self.get_slow_operations()),
            "slow_operations": self.get_slow_operations()
        }
