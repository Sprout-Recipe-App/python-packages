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
        """
        Run deep research using o3-deep-research model.

        Args:
            thread: Thread containing the research prompt
            tools: List of tools to use. At least one data source required:
                - {"type": "web_search_preview"} - Search the web (default)
                - {"type": "file_search", "vector_store_ids": ["vs_..."]} - Search vector stores
                - {"type": "code_interpreter", "container": {"type": "auto"}} - Run code analysis
            **kwargs: Additional parameters:
                - instructions: System instructions for the research
                - max_tool_calls: Limit tool calls to control cost/latency

        Returns:
            Tuple of (result_dict, usage) where result_dict contains:
            - output_text: The final research report with inline citations
            - annotations: List of {url, title, start_index, end_index} for citations
            - tool_calls: List of searches/code executions made
            - status: Final status (completed, failed, etc.)

        Example:
            result, usage = await provider.deep_research(
                thread,
                tools=[{"type": "web_search_preview"}],
                instructions="Be analytical, include statistics and citations."
            )
            print(result["output_text"])
        """
        if not self._deep_research_api:
            return None, None

        return await self._deep_research_api.generate_response(
            thread,
            configuration_name="o3-deep-research",
            tools=tools,
            **kwargs,
        )
