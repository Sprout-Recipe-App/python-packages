from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Any, ClassVar

from pydantic import Field

from database_dimension import MongoDBBaseModel

UTCTimestamp = Annotated[datetime, Field(default_factory=lambda: datetime.now(timezone.utc))]

from .llm_job_step import LLMJobStep
from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJob(MongoDBBaseModel):
    DEFAULT_ESTIMATED_COMPLETION_SECONDS: ClassVar[float] = 60.0
    TERMINAL_STATUSES: ClassVar[list[str]] = ["completed"]
    DEFAULT_FINAL_STATUS: ClassVar[str] = "completed"

    user_id: str
    steps: dict[str, LLMJobStep] = {}
    started_at: UTCTimestamp
    finished_at: datetime | None = None

    @property
    def total_metrics(self) -> "AIPerformanceMetrics":
        return AIPerformanceMetrics.aggregate([step.metrics for step in self.steps.values()])

    def find_step_data_value(self, key: str, latest_first: bool = True) -> Any | None:
        steps = reversed(self.steps.values()) if latest_first else self.steps.values()
        return next((v for s in steps if s.step_data and (v := s.step_data.get(key))), None)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} | {len(self.steps)} steps | ${(metrics := self.total_metrics).cost_dollars:.4f} | {metrics.elapsed_time_seconds:.2f}s"

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
        job = await cls.find_one({"_id": job_id})
        await cls.set_step(
            job_id,
            "workflow_summary",
            LLMJobStep(metrics=job.total_metrics),
            status=cls.DEFAULT_FINAL_STATUS,
            finished_at=datetime.now(timezone.utc),
        )

    @classmethod
    async def get_average_completion_time(cls) -> float:
        pipeline = [
            {"$match": {"status": {"$in": cls.TERMINAL_STATUSES}}},
            {"$sort": {"started_at": -1}},
            {"$limit": 100},
            {
                "$project": {
                    "total_time": {
                        "$sum": {
                            "$map": {
                                "input": {"$objectToArray": "$steps"},
                                "as": "s",
                                "in": "$$s.v.metrics.elapsed_time_seconds",
                            }
                        }
                    }
                }
            },
            {"$group": {"_id": None, "avg_time": {"$avg": "$total_time"}}},
        ]
        cursor = await cls.collection().aggregate(pipeline)
        result = await cursor.to_list(1)
        return result[0]["avg_time"] if result else cls.DEFAULT_ESTIMATED_COMPLETION_SECONDS
