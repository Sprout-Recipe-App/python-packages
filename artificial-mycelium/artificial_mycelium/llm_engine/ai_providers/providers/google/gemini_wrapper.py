import asyncio
from typing import Any

from google import genai
import httpx
from pydantic import TypeAdapter

from dev_pytopia import Logger, with_error_handling

from ..shared.api_utilities import BaseWrapper

_RETRYABLE_CONNECTION_ERRORS = (httpx.ConnectError, httpx.RemoteProtocolError, ConnectionResetError)


@with_error_handling()
class GeminiWrapper(BaseWrapper):
    _UNSUPPORTED_SCHEMA_KEYS = {
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minLength",
        "maxLength",
        "pattern",
        "minItems",
        "maxItems",
        "uniqueItems",
        "minProperties",
        "maxProperties",
        "title",
        "default",
    }

    @classmethod
    def _sanitize_schema(cls, obj, max_enum=64):
        if isinstance(obj, dict):
            if "enum" in obj and len(obj["enum"]) > max_enum:
                sample = ", ".join(str(v) for v in obj["enum"][:10])
                prefix = f"{obj.get('description')}. " if obj.get("description") else ""
                return {
                    "type": obj.get("type", "string"),
                    "description": f"{prefix}Allowed: {sample}, ... ({len(obj['enum'])} values)",
                }
            return {
                k: cls._sanitize_schema(v, max_enum)
                for k, v in obj.items()
                if k not in cls._UNSUPPORTED_SCHEMA_KEYS
            }
        return [cls._sanitize_schema(i, max_enum) for i in obj] if isinstance(obj, list) else obj

    @staticmethod
    def _get_schema(fmt: Any) -> dict | None:
        if hasattr(fmt, "model_json_schema"):
            return fmt.model_json_schema()
        try:
            return TypeAdapter(fmt).json_schema()
        except Exception:
            return None

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> dict[str, Any]:
        gen_config = (
            genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=self._sanitize_schema(schema),
            )
            if (schema := self._get_schema(response_format))
            else None
        )
        return {"contents": thread.get_concatenated_content(), "config": gen_config}

    def _process_response(self, api_response: Any) -> tuple[str, Any]:
        return api_response.text, getattr(api_response, "usage_metadata", None)

    async def _create_api_call(self, parameters: dict, _max_retries: int = 3) -> Any:
        model = parameters.pop("model", "gemini-2.5-flash")
        last_error = None

        for attempt in range(_max_retries):
            try:
                return await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=model,
                    **parameters,
                )
            except _RETRYABLE_CONNECTION_ERRORS as e:
                last_error = e
                delay = 2**attempt
                Logger().warning(f"[GeminiWrapper] Connection error (attempt {attempt + 1}/{_max_retries}): {e}")
                if attempt < _max_retries - 1:
                    await asyncio.sleep(delay)

        raise last_error
