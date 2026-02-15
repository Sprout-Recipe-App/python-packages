import asyncio
import time
from typing import Any

from pydantic import TypeAdapter

from dev_pytopia import Logger

from ....data_models.thread.thread import Thread
from ....services.ai_performance_metrics import AIPerformanceMetrics, record_metrics

DEFAULT_TIMEOUT_CONFIG = {"connect": 10.0, "read": None, "write": 10.0, "pool": 5.0}


class BaseWrapper:
    _retry_preserve_keys: tuple[str, ...] = ()

    def __init__(self, client: Any, model_configurations: dict = None, tier_chains=None):
        self.client = client
        self.configuration_parameters = model_configurations or {}
        self.configuration_tiers = {
            current: next_tier for chain in (tier_chains or []) for current, next_tier in zip(chain, chain[1:])
        }

    @staticmethod
    def get_json_schema(fmt: Any) -> dict | None:
        if hasattr(fmt, "model_json_schema"):
            return fmt.model_json_schema()
        try:
            return TypeAdapter(fmt).json_schema()
        except Exception:
            return None

    async def generate_response(
        self,
        thread,
        configuration_name=None,
        response_format=None,
        log_thread=False,
        metrics_context=None,
        **kwargs,
    ):
        start_time = time.time()
        prepared_request = self._prepare_request(thread, response_format, **kwargs)
        if log_thread and (messages := prepared_request.get("messages")):
            Logger().info(Thread.from_dicts(messages).get_printable_representation())

        response, api_calls = await self._execute_with_retry(prepared_request, configuration_name)
        text, usage = self._process_response(response)
        validate = getattr(response_format, "model_validate_json", None) or (
            lambda t: TypeAdapter(response_format).validate_json(t)
        )
        result = validate(text) if response_format else text

        if not metrics_context:
            return result, usage
        metrics = AIPerformanceMetrics.from_usage(
            usage,
            metrics_context["pricing"],
            time.time() - start_time,
            api_calls=api_calls,
            model_name=metrics_context["model_name"],
            provider_name=metrics_context["provider_name"],
        )
        record_metrics(metrics)
        return result, metrics

    _internal_config_keys = frozenset({"pricing", "timeout"})

    def _prepare_retry_params(self, parameters: dict, next_config: str) -> dict:
        config = {
            k: v
            for k, v in self.configuration_parameters.get(next_config, {}).items()
            if k not in self._internal_config_keys
        }
        return config | {k: parameters[k] for k in self._retry_preserve_keys if k in parameters}

    async def _execute_with_retry(self, parameters: dict, configuration_name: str = None) -> tuple[Any, int]:
        if not configuration_name:
            return await self._create_api_call(parameters)

        total_calls, backoff_delay = 0, None
        while True:
            configuration = self.configuration_parameters[configuration_name]
            parameters["model"] = configuration.get("model", configuration_name)

            try:
                response, calls = await asyncio.wait_for(
                    self._create_api_call(parameters), configuration.get("timeout", 120.0)
                )
                return response, total_calls + calls
            except asyncio.TimeoutError:
                total_calls += 1
                backoff_delay = (backoff_delay or 0.5) * 2
                configuration_name = self.configuration_tiers.get(configuration_name, configuration_name)
                parameters = self._prepare_retry_params(parameters, configuration_name)
                Logger().info(f"Timeout, retrying with {configuration_name} in {backoff_delay:.1f}s")
                await asyncio.sleep(backoff_delay)
