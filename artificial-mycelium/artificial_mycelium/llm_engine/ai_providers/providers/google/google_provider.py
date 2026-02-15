from google import genai

from dev_pytopia import with_error_handling

from .gemini_wrapper import GeminiWrapper
from ...ai_provider_interface import AIProviderInterface

_TEXT_GENERATION_TIERS = ["3-flash"]
_MODEL_CONFIGURATIONS = {
    "3-flash": {"model": "gemini-3-flash-preview", "pricing": {"input": 0.50, "output": 3.00}, "timeout": 360.0},
}


@with_error_handling()
class GoogleProvider(AIProviderInterface):
    _wrapper_class = GeminiWrapper
    _tier_chains = [_TEXT_GENERATION_TIERS]

    def __init__(self, configuration_name):
        super().__init__(configuration_name, _MODEL_CONFIGURATIONS, "GOOGLE_API_KEY")

    def _initialize_client(self, api_key):
        return genai.Client(api_key=api_key)
