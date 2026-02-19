from contextlib import contextmanager
from contextvars import ContextVar
import time
from typing import Any, ClassVar, Self

from pydantic import BaseModel

__all__ = ["AIPerformanceMetrics"]


class AIPerformanceMetrics(BaseModel):
    elapsed_time_seconds: float = 0.0
    cost_dollars: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    api_calls: int = 0
    model_name: str | None = None
    provider_name: str | None = None
    retry_errors: list[str] = []

    _collector: ClassVar[ContextVar[list | None]] = ContextVar("_ai_metrics", default=None)

    def __repr__(self) -> str:
        return f"Metrics(time={self.elapsed_time_seconds:.2f}s, cost=${self.cost_dollars:.6f}, tokens={self.input_tokens + self.output_tokens}, calls={self.api_calls})"

    @classmethod
    def aggregate(cls, items: list[Self], *, elapsed_time: float | None = None) -> Self:
        return cls(
            elapsed_time_seconds=elapsed_time
            if elapsed_time is not None
            else sum(i.elapsed_time_seconds for i in items),
            model_name=items[0].model_name if items else None,
            provider_name=items[0].provider_name if items else None,
            retry_errors=[e for i in items for e in i.retry_errors],
            **{
                k: sum(getattr(i, k) for i in items)
                for k, v in cls.model_fields.items()
                if v.annotation in (int, float) and k != "elapsed_time_seconds"
            },
        )

    @classmethod
    def from_usage(cls, usage: Any, pricing: dict[str, float] | None, elapsed_time: float, **kwargs) -> Self:
        kwargs.setdefault("api_calls", 1)
        if not usage:
            metrics = cls(elapsed_time_seconds=elapsed_time, **kwargs)
        else:
            pricing = pricing or {}
            attr = lambda *keys: next((v for k in keys if (v := getattr(usage, k, None)) is not None), 0)
            input_tokens = attr("input_tokens", "prompt_tokens", "prompt_token_count")
            output_tokens = attr("output_tokens", "completion_tokens", "candidates_token_count")
            cache_hit_tokens = attr("prompt_cache_hit_tokens")
            reasoning_tokens = getattr(
                getattr(usage, "output_tokens_details", None) or getattr(usage, "completion_tokens_details", None),
                "reasoning_tokens",
                0,
            )
            input_price, output_price = pricing.get("input", 0.0), pricing.get("output", 0.0)
            metrics = cls(
                elapsed_time_seconds=elapsed_time,
                cost_dollars=(
                    cache_hit_tokens * pricing.get("cached", input_price)
                    + max(0, input_tokens - cache_hit_tokens) * input_price
                    + output_tokens * output_price
                    + reasoning_tokens * pricing.get("reasoning_output", output_price)
                )
                / 1_000_000,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                cache_hit_tokens=cache_hit_tokens,
                cache_miss_tokens=attr("prompt_cache_miss_tokens"),
                **kwargs,
            )
        if (c := cls._collector.get(None)) is not None:
            c.append(metrics)
        return metrics

    @classmethod
    def timer(cls, **kwargs):
        start = time.time()
        return lambda usage, pricing, **kw: cls.from_usage(usage, pricing, time.time() - start, **kwargs, **kw)

    @classmethod
    @contextmanager
    def collect(cls):
        start, collected = time.time(), []
        token = cls._collector.set(collected)
        try:
            yield collected, lambda: cls.aggregate(collected, elapsed_time=time.time() - start)
        finally:
            cls._collector.reset(token)
