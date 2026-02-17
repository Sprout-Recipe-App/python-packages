from typing import Any

from google import genai
from google.genai.errors import ServerError
import httpx

from dev_pytopia import with_error_handling

from ..shared.api_utilities import BaseProvider
from ....schema_utils import get_json_schema

_MODEL_CONFIGURATIONS = {
    "3-flash": {"model": "gemini-3-flash-preview", "pricing": {"input": 0.50, "output": 3.00}, "timeout": 360.0},
}


@with_error_handling()
class GoogleProvider(BaseProvider):
    _tier_chains = [["3-flash"]]
    _retryable_errors = (httpx.ConnectError, httpx.RemoteProtocolError, ConnectionResetError, ServerError)
    _max_retries = 10

    def __init__(self, configuration_name):
        super().__init__(configuration_name, _MODEL_CONFIGURATIONS, "GOOGLE_API_KEY")

    def _initialize_client(self, api_key):
        return genai.Client(api_key=api_key)

    @classmethod
    def _sanitize_schema(cls, obj, max_enum=64):
        if not isinstance(obj, dict):
            return [cls._sanitize_schema(i, max_enum) for i in obj] if isinstance(obj, list) else obj
        if "enum" in obj and len(obj["enum"]) > max_enum:
            allowed = f"Allowed: {', '.join(map(str, obj['enum'][:10]))}, ... ({len(obj['enum'])} values)"
            return {
                "type": obj.get("type", "string"),
                "description": f"{obj['description']}. {allowed}" if obj.get("description") else allowed,
            }
        return {k: cls._sanitize_schema(v, max_enum) for k, v in obj.items()}

    def _prepare_request(self, thread, response_format: Any = None, **kwargs) -> tuple[dict[str, Any], dict]:
        schema = self._sanitize_schema(get_json_schema(response_format))
        return {
            "contents": thread.get_concatenated_content(),
            "config": genai.types.GenerateContentConfig(
                response_mime_type="application/json", response_json_schema=schema
            )
            if schema
            else None,
        }, {}

    def _process_response(self, api_response: Any) -> tuple[str, Any]:
        return api_response.text, getattr(api_response, "usage_metadata", None)

    async def _create_api_call(self, parameters: dict) -> tuple[Any, int]:
        return await self.client.aio.models.generate_content(**parameters), 1
