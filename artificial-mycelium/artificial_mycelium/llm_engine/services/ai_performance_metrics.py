from functools import reduce
from typing import Any, Self

from pydantic import BaseModel


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

    _NUMERIC_FIELDS = (
        "elapsed_time_seconds",
        "cost_dollars",
        "input_tokens",
        "output_tokens",
        "reasoning_tokens",
        "cache_hit_tokens",
        "cache_miss_tokens",
        "api_calls",
    )

    def __repr__(self) -> str:
        return f"Metrics(time={self.elapsed_time_seconds:.2f}s, cost=${self.cost_dollars:.6f}, tokens={self.input_tokens + self.output_tokens}, calls={self.api_calls})"

    def add(self, other: "AIPerformanceMetrics") -> Self:
        for field in self._NUMERIC_FIELDS:
            setattr(self, field, getattr(self, field) + getattr(other, field))
        return self

    @classmethod
    def aggregate(cls, items: list["AIPerformanceMetrics"]) -> "AIPerformanceMetrics":
        base = cls(
            model_name=items[0].model_name if items else None,
            provider_name=items[0].provider_name if items else None,
        )
        return reduce(lambda result, item: result.add(item), items, base)

    @classmethod
    def from_usage(
        cls, usage: Any, pricing: dict[str, float], elapsed_time: float, **kwargs
    ) -> "AIPerformanceMetrics":
        common = dict(
            elapsed_time_seconds=elapsed_time,
            api_calls=kwargs.get("api_calls", 1),
            model_name=kwargs.get("model_name"),
            provider_name=kwargs.get("provider_name"),
        )
        if not usage:
            return cls(**common)

        def attr(*keys):
            return next((v for k in keys if (v := getattr(usage, k, None)) is not None), 0)

        input_tokens = attr("input_tokens", "prompt_tokens", "prompt_token_count")
        output_tokens = attr("output_tokens", "completion_tokens", "candidates_token_count")
        cache_hit = attr("prompt_cache_hit_tokens")
        details = getattr(usage, "output_tokens_details", None) or getattr(
            usage, "completion_tokens_details", None
        )
        reasoning_tokens = getattr(details, "reasoning_tokens", 0) if details else 0

        cached_rate = pricing.get("cached", pricing.get("input", 0.0))
        cost = (
            cache_hit * cached_rate
            + max(0, input_tokens - cache_hit) * pricing.get("input", 0.0)
            + output_tokens * pricing.get("output", 0.0)
            + reasoning_tokens * pricing.get("reasoning_output", pricing.get("output", 0.0))
        ) / 1_000_000

        return cls(
            **common,
            cost_dollars=cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning_tokens,
            cache_hit_tokens=cache_hit,
            cache_miss_tokens=attr("prompt_cache_miss_tokens"),
        )
