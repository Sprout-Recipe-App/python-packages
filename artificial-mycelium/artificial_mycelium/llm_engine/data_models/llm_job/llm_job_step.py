from typing import Any

from pydantic import BaseModel

from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJobStep(BaseModel):
    metrics: AIPerformanceMetrics = AIPerformanceMetrics()
    step_data: dict[str, Any] = {}
    error_message: str | None = None
