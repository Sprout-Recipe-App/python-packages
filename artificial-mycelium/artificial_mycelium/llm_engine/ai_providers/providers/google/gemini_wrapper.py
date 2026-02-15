import asyncio
import random
from typing import Any

from google import genai
from google.genai.errors import ServerError
import httpx

from dev_pytopia import Logger, with_error_handling

from ..shared.api_utilities import BaseWrapper


@with_error_handling()
class GeminiWrapper(BaseWrapper):
    _RETRYABLE_ERRORS = (httpx.ConnectError, httpx.RemoteProtocolError, ConnectionResetError, ServerError)
    _UNSUPPORTED_SCHEMA_KEYS = set(
        "minimum maximum exclusiveMinimum exclusiveMaximum minLength maxLength pattern "
        "minItems maxItems uniqueItems minProperties maxProperties title default".split()
    )

    @classmethod
    def _sanitize_schema(cls, obj, max_enum=64):
        if isinstance(obj, dict):
            if "enum" in obj and len(obj["enum"]) > max_enum:
                vals = f"Allowed: {', '.join(map(str, obj['enum'][:10]))}, ... ({len(obj['enum'])} values)"
                return {
                    "type": obj.get("type", "string"),
                    "description": f"{obj['description']}. {vals}" if obj.get("description") else vals,
                }
            return {
                k: cls._sanitize_schema(v, max_enum)
                for k, v in obj.items()
                if k not in cls._UNSUPPORTED_SCHEMA_KEYS
            }
        return [cls._sanitize_schema(i, max_enum) for i in obj] if isinstance(obj, list) else obj

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> dict[str, Any]:
        schema = self.get_json_schema(response_format)
        config = (
            genai.types.GenerateContentConfig(
                response_mime_type="application/json", response_json_schema=self._sanitize_schema(schema)
            )
            if schema
            else None
        )
        return {"contents": thread.get_concatenated_content(), "config": config}

    def _process_response(self, api_response: Any) -> tuple[str, Any]:
        return api_response.text, getattr(api_response, "usage_metadata", None)

    async def _create_api_call(self, parameters: dict, _max_retries: int = 10) -> tuple[Any, int]:
        model = parameters.pop("model")
        for attempt in range(_max_retries):
            try:
                return await asyncio.to_thread(
                    self.client.models.generate_content, model=model, **parameters
                ), attempt + 1
            except self._RETRYABLE_ERRORS as e:
                if attempt == _max_retries - 1:
                    raise
                Logger().warning(f"[GeminiWrapper] Retryable error (attempt {attempt + 1}/{_max_retries}): {e}")
                await asyncio.sleep(2 ** min(attempt, 5) + random.uniform(0, 1))
