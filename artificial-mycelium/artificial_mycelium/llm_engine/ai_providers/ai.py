from typing import Any

from .providers.google.google_provider import GoogleProvider
from .providers.openai.openai_provider import OpenAIProvider
from ..data_models.thread.thread import Thread
from ..services.prompt_handler import PromptHandler


class AI:
    _providers = {"openai": OpenAIProvider, "google": GoogleProvider}

    def __init__(self, provider: str = "openai", name: str = "4o", **kwargs):
        self._provider = self._providers[provider](name, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._provider, name)

    @property
    def name(self) -> str:
        return self._provider.configuration_name

    @property
    def provider_name(self) -> str:
        return self._provider.__class__.__name__

    @property
    def configuration(self) -> dict:
        return self._provider.configuration

    async def get_response(self, thread, log_thread=False, **kwargs):
        return await self._provider.get_response(thread, log_thread=log_thread, **kwargs)

    async def get_response_with_prompt(
        self,
        *,
        prompt_location,
        placeholder_values=None,
        role: str = "system",
        response_format=None,
        **kwargs: Any,
    ):
        return await self.get_response(
            Thread.add_first_message(
                role=role,
                text=PromptHandler.build_prompt(
                    prompt_location=prompt_location,
                    placeholder_values=placeholder_values,
                ),
            ),
            response_format=response_format,
            **kwargs,
        )
