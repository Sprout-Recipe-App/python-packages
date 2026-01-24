import asyncio
from collections.abc import Iterable
import json
import re
from typing import Any, get_origin

from pydantic import TypeAdapter

from dev_pytopia import with_error_handling

from ...shared import api_utilities


@with_error_handling()
class ResponsesAPIWrapper(api_utilities.BaseWrapper):
    _retry_preserve_keys = ("input", "text")
    _unwrap_items: bool = False

    @staticmethod
    def _get_schema(fmt: Any) -> dict | None:
        if hasattr(fmt, "model_json_schema"):
            return fmt.model_json_schema()
        try:
            return TypeAdapter(fmt).json_schema()
        except Exception:
            return None

    @staticmethod
    def _get_schema_name(response_format: Any) -> str:
        if hasattr(response_format, "__name__"):
            return response_format.__name__
        if get_origin(response_format) is list:
            args = getattr(response_format, "__args__", ())
            if args and hasattr(args[0], "__name__"):
                return f"{args[0].__name__}List"
        return "Response"

    @classmethod
    def _build_json_schema_format(cls, response_format: Any) -> dict[str, Any] | None:
        if not (schema := cls._get_schema(response_format)):
            return None
        stack = [schema]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if item.get("type") == "object":
                    item.update(additionalProperties=False, required=list(item.get("properties", {}).keys()))
                stack.extend(item.values())
            elif isinstance(item, Iterable) and not isinstance(item, str):
                stack.extend(item)

        if schema.get("type") == "array":
            definitions = schema.pop("$defs", None) or schema.pop("definitions", None)
            schema = {
                "type": "object",
                "properties": {"items": schema},
                "required": ["items"],
                "additionalProperties": False,
            }
            if definitions:
                schema["$defs"] = definitions

        name = re.sub(r"[^a-zA-Z0-9_-]", "_", cls._get_schema_name(response_format))
        return {"format": {"type": "json_schema", "name": name, "strict": True, "schema": schema}}

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> dict[str, Any]:
        parameters = {"input": thread.get_concatenated_content(), **kwargs}
        self._unwrap_items = response_format and get_origin(response_format) is list
        if response_format:
            parameters["text"] = self._build_json_schema_format(response_format) or {"format": response_format}
        return parameters

    def _process_response(self, api_response: Any) -> tuple[str, Any]:
        text = getattr(api_response, "output_text", None)
        if not text:
            for output in getattr(api_response, "output", ()):
                for item in output.content:
                    if hasattr(item, "text"):
                        text = item.text
                        break
                if text:
                    break
        if self._unwrap_items and text:
            text = json.dumps(json.loads(text).get("items", []))
        return text, getattr(api_response, "usage", None)

    async def _create_api_call(self, parameters: dict) -> Any:
        response = await self.client.responses.create(**parameters)
        while response.status in ("queued", "in_progress"):
            await asyncio.sleep(2)
            response = await self.client.responses.retrieve(response.id)
        return response
