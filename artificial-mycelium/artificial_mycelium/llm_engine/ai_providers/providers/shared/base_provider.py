import asyncio
import os
from typing import Any

from pydantic import TypeAdapter

from ....services.ai_performance_metrics import AIPerformanceMetrics


class BaseProvider:
    _retryable_errors: tuple[type[Exception], ...] = ()

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self.configuration = model_configurations.get(configuration_name, {})
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var)) else None
        self._metrics_kwargs = {
            "model_name": configuration_name,
            "provider_name": type(self).__name__.replace("Provider", ""),
        }

    async def get_response(self, thread, **kwargs):
        track, fmt = AIPerformanceMetrics.timer(**self._metrics_kwargs), kwargs.pop("response_format", None)
        request, post_process = self._prepare_request(thread, fmt, **kwargs)
        request["model"] = self.configuration.get("model", self.configuration_name)
        cfg = self.configuration.get
        result, retry_info = await self._execute_with_retry(request, cfg("timeout", 120.0))
        if error := retry_info.pop("error", None):
            track(None, cfg("pricing"), **retry_info)
            raise error
        text, usage = self._process_response(result, **post_process)
        metrics = track(usage, cfg("pricing"), **retry_info)
        return (TypeAdapter(fmt).validate_json(text) if fmt else text), metrics

    async def _execute_with_retry(self, params: dict, timeout: float) -> tuple[Any, dict]:
        retries = []
        while True:
            try:
                return await asyncio.wait_for(self._create_api_call(params), timeout), {
                    "api_calls": len(retries) + 1,
                    "retry_errors": retries,
                }
            except (asyncio.TimeoutError, *self._retryable_errors) as e:
                retries.append(type(e).__name__)
                await asyncio.sleep(2 ** len(retries))
