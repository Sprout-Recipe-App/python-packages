from abc import ABC, abstractmethod
import os


class AIProviderInterface(ABC):
    _wrapper_class = None
    _tier_chains: list[list[str]] = []

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self._model_configurations = model_configurations
        self.configuration = model_configurations.get(configuration_name, {})
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var)) else None
        self.model_name = self.configuration.get("model", configuration_name)
        self._api_wrapper = (
            self._wrapper_class(self.client, self._model_configurations, self._tier_chains)
            if self.client and self._wrapper_class
            else None
        )

    async def get_response(self, thread, log_thread=False, **kwargs):
        metrics_context = (
            {
                "pricing": self.configuration.get("pricing"),
                "model_name": self.configuration_name,
                "provider_name": type(self).__name__.replace("Provider", ""),
            }
            if kwargs.pop("with_metrics", False)
            else None
        )

        return await self._api_wrapper.generate_response(
            thread,
            configuration_name=self.configuration_name,
            log_thread=log_thread,
            metrics_context=metrics_context,
            **kwargs,
        )

    @abstractmethod
    def _initialize_client(self, api_key): ...
