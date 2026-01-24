from datetime import datetime, timezone
from typing import Any

from pydantic import Field

from database_dimension import MongoDBBaseModel

from .llm_job_step import LLMJobStep
from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJob(MongoDBBaseModel):
    user_id: str
    processing_steps: list[LLMJobStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    @property
    def total_metrics(self) -> "AIPerformanceMetrics":
        from ...services.ai_performance_metrics import AIPerformanceMetrics

        return AIPerformanceMetrics.aggregate([s.metrics for s in self.processing_steps])

    @property
    def visible_steps(self) -> list[LLMJobStep]:
        return [step for step in self.processing_steps if step.step_name != LLMJobStep.WORKFLOW_SUMMARY]

    def get_step_data(self, key: str, reverse: bool = True) -> Any | None:
        steps = reversed(self.processing_steps) if reverse else self.processing_steps
        return next((value for step in steps if (value := step.get(key))), None)

    def __str__(self) -> str:
        m = self.total_metrics
        return f"{self.__class__.__name__} | {len(self.processing_steps)} steps | ${m.cost_dollars:.4f} | {m.elapsed_time_seconds:.2f}s"
