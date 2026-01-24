from dev_pytopia import with_error_handling

from . import constants
from .chat_completions_wrapper import ChatCompletionsWrapper
from ..shared.openai_compatible_provider import OpenAICompatibleProvider


@with_error_handling()
class DeepSeekProvider(OpenAICompatibleProvider):
    _base_url = constants.BASE_URL
    _wrapper_class = ChatCompletionsWrapper
    _tier_chains = [constants.TEXT_GENERATION_TIERS]

    def __init__(self, configuration_name):
        super().__init__(
            configuration_name, constants.MODEL_CONFIGURATIONS, constants.API_KEY_ENVIRONMENT_VARIABLE_NAME
        )
