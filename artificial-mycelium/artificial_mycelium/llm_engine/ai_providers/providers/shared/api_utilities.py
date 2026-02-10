import asyncio
import time
from typing import Any

from pydantic import TypeAdapter

from dev_pytopia import Logger

from ....data_models.thread.thread import Thread
from ....services.ai_performance_metrics import AIPerformanceMetrics

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
        configuration_name: str = None,
        response_format: Any = None,
        log_thread: bool = False,
        metrics_context: dict = None,
        **kwargs,
    ):
        start_time = time.time()

        prepared_request = self._prepare_request(thread, response_format, **kwargs)
        if log_thread and (messages := prepared_request.get("messages")):
            Logger().info(Thread.from_dicts(messages).get_printable_representation())

        text, usage = self._process_response(await self._execute_with_retry(prepared_request, configuration_name))
        result = (
            text
            if not response_format
            else (
                response_format.model_validate_json(text)
                if hasattr(response_format, "model_validate_json")
                else TypeAdapter(response_format).validate_json(text)
            )
        )
        elapsed = time.time() - start_time

        if not metrics_context:
            return result, usage

        return result, AIPerformanceMetrics.from_usage(
            usage,
            metrics_context["pricing"],
            elapsed,
            model_name=metrics_context["model_name"],
            provider_name=metrics_context["provider_name"],
        )

    _internal_config_keys = frozenset({"pricing", "timeout"})

    def _prepare_retry_params(self, parameters: dict, next_configuration: str) -> dict:
        preserved = {key: parameters[key] for key in self._retry_preserve_keys if key in parameters}
        config = {
            k: v
            for k, v in self.configuration_parameters.get(next_configuration, {}).items()
            if k not in self._internal_config_keys
        }
        return config | preserved

    async def _execute_with_retry(self, parameters: dict, configuration_name: str = None) -> Any:
        if not configuration_name:
            return await self._create_api_call(parameters)

        backoff_delay = None
        while True:
            configuration = self.configuration_parameters[configuration_name]
            parameters["model"] = configuration.get("model", configuration_name)

            try:
                return await asyncio.wait_for(
                    self._create_api_call(parameters), configuration.get("timeout", 120.0)
                )
            except asyncio.TimeoutError:
                backoff_delay = 1.0 if backoff_delay is None else backoff_delay * 2
                configuration_name = self.configuration_tiers.get(configuration_name, configuration_name)
                parameters = self._prepare_retry_params(parameters, configuration_name)
                Logger().info(f"Timeout, retrying with {configuration_name} in {backoff_delay:.1f}s")
                await asyncio.sleep(backoff_delay)
