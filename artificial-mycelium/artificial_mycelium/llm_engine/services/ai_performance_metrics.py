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

    def __repr__(self) -> str:
        return f"Metrics(time={self.elapsed_time_seconds:.2f}s, cost=${self.cost_dollars:.6f}, tokens={self.input_tokens + self.output_tokens}, calls={self.api_calls})"

    @classmethod
    def aggregate(cls, items: list["AIPerformanceMetrics"]) -> "AIPerformanceMetrics":
        numeric = [k for k, v in cls.model_fields.items() if v.annotation in (int, float)]
        return cls(
            model_name=items[0].model_name if items else None,
            provider_name=items[0].provider_name if items else None,
            **{f: sum(getattr(i, f) for i in items) for f in numeric},
        )

    @classmethod
    def from_usage(cls, usage: Any, pricing: dict[str, float], elapsed_time: float, **kwargs) -> Self:
        def attr(*keys):
            return next((v for k in keys if (v := getattr(usage, k, None)) is not None), 0)

        if not usage:
            return cls(elapsed_time_seconds=elapsed_time, api_calls=kwargs.get("api_calls", 1), **kwargs)

        input_tokens = attr("input_tokens", "prompt_tokens", "prompt_token_count")
        output_tokens = attr("output_tokens", "completion_tokens", "candidates_token_count")
        cache_hit = attr("prompt_cache_hit_tokens")
        details = getattr(usage, "output_tokens_details", None) or getattr(
            usage, "completion_tokens_details", None
        )
        reasoning = getattr(details, "reasoning_tokens", 0) if details else 0

        cost = (
            cache_hit * pricing.get("cached", pricing.get("input", 0.0))
            + max(0, input_tokens - cache_hit) * pricing.get("input", 0.0)
            + output_tokens * pricing.get("output", 0.0)
            + reasoning * pricing.get("reasoning_output", pricing.get("output", 0.0))
        ) / 1_000_000

        return cls(
            elapsed_time_seconds=elapsed_time,
            api_calls=kwargs.get("api_calls", 1),
            model_name=kwargs.get("model_name"),
            provider_name=kwargs.get("provider_name"),
            cost_dollars=cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            reasoning_tokens=reasoning,
            cache_hit_tokens=cache_hit,
            cache_miss_tokens=attr("prompt_cache_miss_tokens"),
        )
