from abc import abstractmethod
import asyncio
import os
import random
import time
from typing import Any

from pydantic import TypeAdapter

from dev_pytopia import Logger

from ....data_models.thread.thread import Thread
from ....services.ai_performance_metrics import AIPerformanceMetrics, record_metrics


class BaseProvider:
    _retry_preserve_keys: tuple[str, ...] = ()
    _retryable_errors: tuple[type[Exception], ...] = ()
    _tier_chains: list[list[str]] = []
    _internal_config_keys = frozenset({"pricing", "timeout"})
    _max_retries: int = 5

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self.configuration = model_configurations.get(configuration_name, {})
        self.model_name = self.configuration.get("model", configuration_name)
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var)) else None
        self._model_configurations = model_configurations
        self._configuration_tiers = {
            current: next_tier for chain in self._tier_chains for current, next_tier in zip(chain, chain[1:])
        }

    async def get_response(self, thread, log_thread=False, **kwargs):
        with_metrics = kwargs.pop("with_metrics", False)
        response_format = kwargs.pop("response_format", None)
        start_time = time.time()
        prepared_request = self._prepare_request(thread, response_format, **kwargs)
        post_process = prepared_request.pop("_post_process", {})
        if log_thread and (messages := prepared_request.get("messages")):
            Logger().info(Thread.from_dicts(messages).get_printable_representation())

        response, api_calls = await self._execute_with_retry(prepared_request)
        text, usage = self._process_response(response, **post_process)
        result = (
            (getattr(response_format, "model_validate_json", None) or TypeAdapter(response_format).validate_json)(
                text
            )
            if response_format
            else text
        )
        if with_metrics:
            usage = AIPerformanceMetrics.from_usage(
                usage,
                self.configuration.get("pricing"),
                time.time() - start_time,
                api_calls=api_calls,
                model_name=self.configuration_name,
                provider_name=type(self).__name__.replace("Provider", ""),
            )
            record_metrics(usage)
        return result, usage

    async def _execute_with_retry(self, parameters: dict) -> tuple[Any, int]:
        retryable = (asyncio.TimeoutError, *self._retryable_errors)
        total_calls, config_name, retries = 0, self.configuration_name, 0
        while True:
            config = self._model_configurations[config_name]
            parameters["model"] = config.get("model", config_name)
            try:
                response, calls = await asyncio.wait_for(
                    self._create_api_call(parameters), config.get("timeout", 120.0)
                )
                return response, total_calls + calls
            except retryable as e:
                retries += 1
                if retries >= self._max_retries:
                    raise
                total_calls += 1
                if isinstance(e, asyncio.TimeoutError):
                    config_name = self._configuration_tiers.get(config_name, config_name)
                    cfg = self._model_configurations.get(config_name, {})
                    parameters = {k: v for k, v in cfg.items() if k not in self._internal_config_keys} | {
                        k: parameters[k] for k in self._retry_preserve_keys if k in parameters
                    }
                delay = min(2**retries, 32) + random.uniform(0, 1)
                Logger().info(f"Retrying with {config_name} in {delay:.1f}s ({type(e).__name__})")
                await asyncio.sleep(delay)

    @abstractmethod
    def _initialize_client(self, api_key): ...

    @abstractmethod
    def _prepare_request(self, thread, response_format=None, **kwargs): ...

    @abstractmethod
    def _process_response(self, api_response, **process_options): ...

    @abstractmethod
    def _create_api_call(self, parameters: dict): ...
