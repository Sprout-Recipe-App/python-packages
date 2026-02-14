from functools import cached_property

from dev_pytopia import with_error_handling

from . import constants
from .service_wrappers.deep_research_wrapper import DeepResearchWrapper
from .service_wrappers.image_api_wrapper import ImageAPIWrapper
from .service_wrappers.responses_api_wrapper import ResponsesAPIWrapper
from ..shared.openai_compatible_provider import OpenAICompatibleProvider


@with_error_handling()
class OpenAIProvider(OpenAICompatibleProvider):
    _wrapper_class = ResponsesAPIWrapper
    _tier_chains = [
        constants.TEXT_GENERATION_TIERS,
        constants.IMAGE_GENERATION_TIERS,
        constants.DEEP_RESEARCH_TIERS,
    ]

    def __init__(self, configuration_name):
        super().__init__(
            configuration_name, constants.MODEL_CONFIGURATIONS, constants.API_KEY_ENVIRONMENT_VARIABLE_NAME
        )

    @cached_property
    def _image_api(self):
        return ImageAPIWrapper(self.client, self._model_configurations) if self.client else None

    @cached_property
    def _deep_research_api(self):
        return DeepResearchWrapper(self.client, self._model_configurations) if self.client else None

    async def generate_image(self, prompt, **kwargs):
        return await self._image_api.generate(self.model_name, prompt, **kwargs) if self._image_api else None

    async def edit_image(self, image, prompt, **kwargs):
        return await self._image_api.edit(self.model_name, image, prompt, **kwargs) if self._image_api else None

    async def deep_research(self, thread, tools: list[dict] = None, **kwargs):
        if not self._deep_research_api:
            return None, None

        return await self._deep_research_api.generate_response(
            thread,
            configuration_name="o3-deep-research",
            tools=tools,
            **kwargs,
        )
