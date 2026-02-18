import asyncio
import os
import random
import time
from typing import Any

from pydantic import TypeAdapter

from ....services.ai_performance_metrics import MetricsTracker


class BaseProvider:
    _retryable_errors: tuple[type[Exception], ...] = ()
    _max_retries: int = 5

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self.configuration = model_configurations.get(configuration_name, {})
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var)) else None

    async def get_response(self, thread, **kwargs):
        response_format = kwargs.pop("response_format", None)
        start_time = time.time()
        request, post_process = self._prepare_request(thread, response_format, **kwargs)
        request["model"] = self.configuration.get("model", self.configuration_name)
        result, retry_info = await self._execute_with_retry(request, self.configuration.get("timeout", 120.0))
        error = retry_info.pop("error", None)
        track = lambda usage: MetricsTracker.track(
            usage,
            self.configuration.get("pricing"),
            time.time() - start_time,
            model_name=self.configuration_name,
            provider_name=type(self).__name__.replace("Provider", ""),
            **retry_info,
        )
        if error:
            track(None)
            raise error
        text, usage = self._process_response(result, **post_process)
        parsed = TypeAdapter(response_format).validate_json(text) if response_format else text
        return parsed, track(usage)

    async def _execute_with_retry(self, parameters: dict, timeout: float) -> tuple[Any | None, dict]:
        errors, last_exc = [], None
        for attempt in range(self._max_retries):
            try:
                return await asyncio.wait_for(self._create_api_call(parameters), timeout), {
                    "api_calls": attempt + 1,
                    "retry_errors": errors,
                }
            except (asyncio.TimeoutError, *self._retryable_errors) as e:
                errors.append(type(e).__name__)
                last_exc = e
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(min(2 ** (attempt + 1), 32) + random.uniform(0, 1))
        return None, {"api_calls": self._max_retries, "retry_errors": errors, "error": last_exc}
