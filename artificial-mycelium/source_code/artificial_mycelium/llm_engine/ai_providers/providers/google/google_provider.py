from functools import cached_property

from google import genai

from dev_pytopia import with_error_handling

from . import constants
from .gemini_wrapper import GeminiWrapper
from ...ai_provider_interface import AIProviderInterface


@with_error_handling()
class GoogleProvider(AIProviderInterface):
    _tier_chains = [constants.TEXT_GENERATION_TIERS]

    def __init__(self, configuration_name):
        super().__init__(
            configuration_name, constants.MODEL_CONFIGURATIONS, constants.API_KEY_ENVIRONMENT_VARIABLE_NAME
        )

    def _initialize_client(self, api_key):
        return genai.Client(api_key=api_key)

    @cached_property
    def _api_wrapper(self):
        return GeminiWrapper(self.client, self._model_configurations, self._tier_chains) if self.client else None
