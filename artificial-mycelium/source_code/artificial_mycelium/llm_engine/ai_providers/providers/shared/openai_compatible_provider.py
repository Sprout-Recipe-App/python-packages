import httpx
from openai import AsyncOpenAI

from .api_utilities import DEFAULT_TIMEOUT_CONFIG
from ...ai_provider_interface import AIProviderInterface


class OpenAICompatibleProvider(AIProviderInterface):
    _base_url: str | None = None

    def _initialize_client(self, api_key):
        return AsyncOpenAI(
            api_key=api_key, base_url=self._base_url, timeout=httpx.Timeout(**DEFAULT_TIMEOUT_CONFIG)
        )
