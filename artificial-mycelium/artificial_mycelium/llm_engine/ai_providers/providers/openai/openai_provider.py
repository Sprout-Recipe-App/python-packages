import asyncio
import json
from typing import Any, get_origin

import httpx
from openai import AsyncOpenAI

from dev_pytopia import with_error_handling

from ..shared.base_provider import BaseProvider
from ....schema_utils import get_json_schema

_CONFIGS = [
    ("5-nano", "gpt-5-nano", None, 0.05, 0.40, 360),
    ("5-mini-minimal", "gpt-5-mini", "minimal", 0.25, 2.00, 360),
    ("5-mini-low", "gpt-5-mini", "low", 0.25, 2.00, 360),
    ("5-mini", "gpt-5-mini", None, 0.25, 2.00, 360),
    ("5-mini-high", "gpt-5-mini", "high", 0.25, 2.00, 360),
    ("5-minimal", "gpt-5", "minimal", 1.25, 10.00, 360),
    ("5-low", "gpt-5", "low", 1.25, 10.00, 360),
    ("5.1", "gpt-5.1", None, 1.25, 10.00, 600),
    ("5.2", "gpt-5.2", None, 1.75, 14.00, 600),
    ("5-high", "gpt-5", "high", 1.25, 10.00, 1200),
    ("5-pro", "gpt-5-pro", None, 15.00, 120.00, 1800, True),
    ("5.2-pro-medium", "gpt-5.2-pro", "medium", 21.00, 168.00, 1800, True),
    ("5.2-pro-high", "gpt-5.2-pro", "high", 21.00, 168.00, 1800, True),
    ("5.2-pro-xhigh", "gpt-5.2-pro", "xhigh", 21.00, 168.00, 1800, True),
]


def _build(name, model, effort, price_in, price_out, timeout, background=False):
    return name, {
        "model": model,
        "pricing": {"input": price_in, "output": price_out},
        "timeout": timeout,
        **({"reasoning": {"effort": effort}} if effort else {}),
        **({"background": True} if background else {}),
    }


_MODEL_CONFIGURATIONS = dict(_build(*row) for row in _CONFIGS)
_DEFAULT_TIMEOUT_CONFIG = {"connect": 10.0, "read": None, "write": 10.0, "pool": 5.0}
_API_KEY_ENVIRONMENT_VARIABLE_NAME = "OPENAI_API_KEY"


@with_error_handling()
class OpenAIProvider(BaseProvider):
    def __init__(self, configuration_name):
        super().__init__(configuration_name, _MODEL_CONFIGURATIONS, _API_KEY_ENVIRONMENT_VARIABLE_NAME)

    def _initialize_client(self, api_key):
        return AsyncOpenAI(api_key=api_key, timeout=httpx.Timeout(**_DEFAULT_TIMEOUT_CONFIG))

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> tuple[dict[str, Any], dict]:
        params = {"input": thread.get_concatenated_content(), **kwargs}
        post_process = {}
        if not response_format:
            return params, post_process
        if get_origin(response_format) is list:
            post_process = {"unwrap_items": True}
        schema = get_json_schema(response_format)
        if not schema:
            params["text"] = {"format": response_format}
            return params, post_process
        stack = [schema]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if item.get("type") == "object":
                    item.update(additionalProperties=False, required=list(item.get("properties", {}).keys()))
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
        if schema.get("type") == "array":
            defs = schema.pop("$defs", None) or schema.pop("definitions", None)
            schema = {
                "type": "object",
                "properties": {"items": schema},
                "required": ["items"],
                "additionalProperties": False,
                **({"$defs": defs} if defs else {}),
            }
        args = getattr(response_format, "__args__", ())
        name = getattr(response_format, "__name__", None) or (
            f"{args[0].__name__}List"
            if get_origin(response_format) is list and args and hasattr(args[0], "__name__")
            else "Response"
        )
        params["text"] = {
            "format": {
                "type": "json_schema",
                "strict": True,
                "schema": schema,
                "name": "".join(c if c.isalnum() or c in "_-" else "_" for c in name),
            }
        }
        return params, post_process

    def _process_response(self, api_response: Any, *, unwrap_items=False) -> tuple[str, Any]:
        text = api_response.output_text
        return (
            json.dumps(json.loads(text).get("items", [])) if unwrap_items and text else text
        ), api_response.usage

    async def _create_api_call(self, parameters: dict):
        response = await self.client.responses.create(**parameters)
        while response.status in ("queued", "in_progress"):
            response = await asyncio.sleep(2) or await self.client.responses.retrieve(response.id)
        return response
