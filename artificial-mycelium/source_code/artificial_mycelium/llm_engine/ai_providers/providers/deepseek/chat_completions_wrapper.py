from typing import Any

from pydantic import TypeAdapter

from dev_pytopia import with_error_handling

from ..shared import api_utilities
from ....services.prompt_handler import PromptHandler


@with_error_handling()
class ChatCompletionsWrapper(api_utilities.BaseWrapper):
    _retry_preserve_keys = ("messages", "response_format")

    @staticmethod
    def _has_schema(fmt: Any) -> bool:
        if hasattr(fmt, "model_json_schema"):
            return True
        try:
            TypeAdapter(fmt).json_schema()
            return True
        except Exception:
            return False

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> dict[str, Any]:
        messages = thread.get_messages_as_dicts()
        if self._has_schema(response_format) and messages and messages[-1].get("role") in ("user", "system"):
            messages[-1]["content"] = PromptHandler.build_prompt_with_schema(
                messages[-1]["content"], response_format
            )
        return {
            "messages": messages,
            **kwargs,
            **({"response_format": {"type": "json_object"}} if response_format else {}),
        }

    def _process_response(self, api_response: Any) -> tuple[str, Any]:
        return api_response.choices[0].message.content, getattr(api_response, "usage", None)

    async def _create_api_call(self, parameters: dict) -> Any:
        return await self.client.chat.completions.create(**parameters)
