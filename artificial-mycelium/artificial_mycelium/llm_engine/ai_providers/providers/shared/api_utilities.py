import asyncio
import os
import random
import time
from typing import Any

from pydantic import TypeAdapter

from dev_pytopia import Logger

from ....services.ai_performance_metrics import MetricsTracker


class BaseProvider:
    _retry_preserve_keys: tuple[str, ...] = ()
    _retryable_errors: tuple[type[Exception], ...] = ()
    _tier_chains: list[list[str]] = []
    _internal_config_keys = frozenset({"pricing", "timeout"})
    _max_retries: int = 5

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self.configuration = model_configurations.get(configuration_name, {})
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var)) else None
        self._model_configurations = model_configurations
        self._configuration_tiers = {
            current: next_tier for chain in self._tier_chains for current, next_tier in zip(chain, chain[1:])
        }

    async def get_response(self, thread, log_thread=False, **kwargs):
        response_format, start_time = kwargs.pop("response_format", None), time.time()
        if log_thread:
            Logger().info(thread.get_printable_representation())
        request, post_process = self._prepare_request(thread, response_format, **kwargs)
        response, api_calls = await self._execute_with_retry(request)
        text, usage = self._process_response(response, **post_process)
        if response_format:
            text = (
                getattr(response_format, "model_validate_json", None) or TypeAdapter(response_format).validate_json
            )(text)
        return text, MetricsTracker.track(
            usage,
            self.configuration.get("pricing"),
            time.time() - start_time,
            api_calls=api_calls,
            model_name=self.configuration_name,
            provider_name=type(self).__name__.replace("Provider", ""),
        )

    async def _execute_with_retry(self, parameters: dict) -> tuple[Any, int]:
        configs, config_name = self._model_configurations, self.configuration_name
        parameters["model"] = configs[config_name].get("model", config_name)
        for attempt in range(self._max_retries):
            try:
                response, calls = await asyncio.wait_for(
                    self._create_api_call(parameters), configs[config_name].get("timeout", 120.0)
                )
                return response, attempt + calls
            except (asyncio.TimeoutError, *self._retryable_errors) as e:
                if attempt == self._max_retries - 1:
                    raise
                if isinstance(e, asyncio.TimeoutError) and config_name in self._configuration_tiers:
                    config_name = self._configuration_tiers[config_name]
                    cfg = configs.get(config_name, {})
                    parameters = (
                        {k: v for k, v in cfg.items() if k not in self._internal_config_keys}
                        | {k: parameters[k] for k in self._retry_preserve_keys if k in parameters}
                        | {"model": cfg.get("model", config_name)}
                    )
                delay = min(2 ** (attempt + 1), 32) + random.uniform(0, 1)
                Logger().info(f"Retrying with {config_name} in {delay:.1f}s ({type(e).__name__})")
                await asyncio.sleep(delay)
