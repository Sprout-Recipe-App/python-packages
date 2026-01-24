from contextlib import asynccontextmanager
from datetime import datetime, timezone

from database_dimension import DataModelHandler

from .llm_job import LLMJob
from .llm_job_step import LLMJobStep
from ...services.ai_performance_metrics import AIPerformanceMetrics


class LLMJobHandler(DataModelHandler):
    MODEL_TYPE: type[LLMJob] = LLMJob
    TERMINAL_STATUSES: list[str] = ["completed"]
    DEFAULT_FINAL_STATUS: str = "completed"
    DEFAULT_ESTIMATED_COMPLETION_SECONDS: float = 150.0

    @classmethod
    async def add_step(cls, job_id: str, step: LLMJobStep, **extra_set_fields) -> None:
        update = {
            "$push": {"processing_steps": step.model_dump()},
            **({"$set": extra_set_fields} if extra_set_fields else {}),
        }
        await cls.update_one({"_id": job_id}, update)

    @classmethod
    async def update_step_by_name(cls, job_id: str, step_name: str, update_dict: dict) -> None:
        set_ops = {f"processing_steps.$[step].{key}": value for key, value in update_dict.items()}
        await cls.collection().update_one(
            cls._normalize_query({"_id": job_id}), {"$set": set_ops}, array_filters=[{"step.step_name": step_name}]
        )

    @classmethod
    @asynccontextmanager
    async def track_step(cls, job_id: str, step_name: str, **extra_set_fields):
        await cls.add_step(job_id, LLMJobStep(step_name=step_name), **extra_set_fields)
        tracker = {}
        try:
            yield tracker
        except Exception as e:
            tracker["error_message"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            if tracker:
                await cls.update_step_by_name(job_id, step_name, tracker)

    @classmethod
    async def add_workflow_summary(cls, job_id: str) -> None:
        job = await cls.load_by_id(job_id)
        await cls.add_step(
            job_id,
            LLMJobStep(
                step_name=LLMJobStep.WORKFLOW_SUMMARY,
                metrics=AIPerformanceMetrics.aggregate([s.metrics for s in job.processing_steps]),
            ),
            status=cls.DEFAULT_FINAL_STATUS,
            completed_at=datetime.now(timezone.utc),
        )

    @classmethod
    async def get_average_completion_time(cls) -> float:
        pipeline = [
            {"$match": {"status": {"$in": cls.TERMINAL_STATUSES}}},
            {"$sort": {"created_at": -1}},
            {"$limit": 100},
            {"$project": {"total_time": {"$sum": "$processing_steps.metrics.elapsed_time_seconds"}}},
            {"$group": {"_id": None, "avg_time": {"$avg": "$total_time"}}},
        ]
        result = await cls.collection().aggregate(pipeline).to_list(1)
        return result[0]["avg_time"] if result else cls.DEFAULT_ESTIMATED_COMPLETION_SECONDS
