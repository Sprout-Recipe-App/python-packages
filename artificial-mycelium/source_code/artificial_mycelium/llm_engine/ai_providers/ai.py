from typing import Any

from .providers.deepseek.deepseek_provider import DeepSeekProvider
from .providers.google.google_provider import GoogleProvider
from .providers.openai.openai_provider import OpenAIProvider
from ..data_models.thread.thread import Thread
from ..services.prompt_handler import PromptHandler


class AI:
    _providers = {"openai": OpenAIProvider, "deepseek": DeepSeekProvider, "google": GoogleProvider}

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
        return getattr(self._provider, "configuration", {})

    async def get_response(self, thread, log_thread=False, **kwargs):
        metrics_context = {
            "pricing": self.configuration.get("pricing"),
            "model_name": self.name,
            "provider_name": self.provider_name.replace("Provider", ""),
        } if kwargs.pop("with_metrics", False) else None

        return await self._provider._api_wrapper.generate_response(
            thread,
            configuration_name=self.name,
            log_thread=log_thread,
            metrics_context=metrics_context,
            **kwargs,
        )

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
