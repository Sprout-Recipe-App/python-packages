from typing import Any, ClassVar

from pydantic import BaseModel, Field

from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJobStep(BaseModel):
    WORKFLOW_SUMMARY: ClassVar[str] = "workflow_summary"
    step_name: str
    metrics: AIPerformanceMetrics = Field(default_factory=AIPerformanceMetrics)
    step_data: dict[str, Any] | None = None
    error_message: str | None = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.step_data.get(key, default) if self.step_data else default
