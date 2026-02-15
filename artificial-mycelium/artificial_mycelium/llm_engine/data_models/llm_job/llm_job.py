from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, ClassVar

from pydantic import Field

from database_dimension import MongoDBBaseModel

from .llm_job_step import LLMJobStep
from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJob(MongoDBBaseModel):
    TERMINAL_STATUSES: ClassVar[list[str]] = ["completed"]
    DEFAULT_FINAL_STATUS: ClassVar[str] = "completed"
    SUMMARY_STEP_NAME: ClassVar[str] = "workflow_summary"

    user_id: str
    steps: dict[str, LLMJobStep] = {}
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def find_step_data_value(self, key: str) -> Any:
        return next((s.step_data[key] for s in reversed(self.steps.values()) if key in s.step_data), None)

    @classmethod
    async def set_step(cls, job_id: str, step_name: str, step: LLMJobStep, **extra) -> None:
        await cls.update_one({"_id": job_id}, {"$set": {f"steps.{step_name}": step.model_dump(), **extra}})

    @classmethod
    async def update_step(cls, job_id: str, step_name: str, updates: dict) -> None:
        await cls.update_one({"_id": job_id}, {"$set": {f"steps.{step_name}.{k}": v for k, v in updates.items()}})

    @classmethod
    @asynccontextmanager
    async def track_step(cls, job_id: str, step_name: str, **extra):
        await cls.set_step(job_id, step_name, LLMJobStep(), **extra)
        tracker = {}
        try:
            yield tracker
        except Exception as e:
            tracker["error_message"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            if tracker:
                await cls.update_step(job_id, step_name, tracker)

    @classmethod
    async def add_workflow_summary(cls, job_id: str) -> None:
        if not (job := await cls.find_one(job_id)):
            return
        elapsed = (datetime.now(UTC) - job.started_at).total_seconds()
        metrics = AIPerformanceMetrics.aggregate([s.metrics for s in job.steps.values()], elapsed_time=elapsed)
        await cls.set_step(
            job_id, cls.SUMMARY_STEP_NAME, LLMJobStep(metrics=metrics), status=cls.DEFAULT_FINAL_STATUS
        )
