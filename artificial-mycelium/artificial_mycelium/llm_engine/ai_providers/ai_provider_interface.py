from abc import ABC, abstractmethod
from functools import cached_property
import os


class AIProviderInterface(ABC):
    _wrapper_class = None
    _tier_chains: list[list[str]] = []

    def __init__(self, configuration_name, model_configurations, api_key_env_var):
        self.configuration_name = configuration_name
        self._model_configurations = model_configurations
        self.configuration = model_configurations.get(configuration_name, {})
        self.client = self._initialize_client(api_key) if (api_key := os.getenv(api_key_env_var or "")) else None

    @abstractmethod
    def _initialize_client(self, api_key): ...

    @property
    def model_name(self) -> str:
        return self.configuration.get("model", self.configuration_name)

    @cached_property
    def _api_wrapper(self):
        return (
            self._wrapper_class(self.client, self._model_configurations, self._tier_chains)
            if self.client and self._wrapper_class
            else None
        )
