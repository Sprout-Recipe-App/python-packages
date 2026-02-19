from .providers.google.google_provider import GoogleProvider
from .providers.openai.openai_provider import OpenAIProvider
from ..data_models.thread.thread import Thread
from ..services.prompt_handler import PromptHandler


class AI:
    _providers = {"openai": OpenAIProvider, "google": GoogleProvider}

    def __init__(self, provider, name, **kwargs):
        self._provider = self._providers[provider](name, **kwargs)

    @property
    def name(self):
        return self._provider.configuration_name

    async def get_response(self, thread, **kwargs):
        return await self._provider.get_response(thread, **kwargs)

    async def get_response_with_prompt(
        self, *, prompt_location, placeholder_values=None, role="system", response_format=None, **kwargs
    ):
        prompt = PromptHandler.build_prompt(prompt_location=prompt_location, placeholder_values=placeholder_values)
        return await self.get_response(
            Thread.add_first_message(role=role, text=prompt),
            response_format=response_format,
            **kwargs,
        )
