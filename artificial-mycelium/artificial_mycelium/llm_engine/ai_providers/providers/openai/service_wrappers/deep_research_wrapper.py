import asyncio
import time
from typing import Any

from dev_pytopia import Logger, with_error_handling

from ...shared import api_utilities


@with_error_handling()
class DeepResearchWrapper(api_utilities.BaseWrapper):
    _retry_preserve_keys = ("input", "tools", "instructions")

    async def generate_response(
        self,
        thread,
        configuration_name: str = None,
        tools: list[dict] = None,
        **kwargs,
    ):
        start_time = time.time()

        if tools is None:
            tools = [{"type": "web_search_preview"}]

        parameters = {
            "input": thread.get_concatenated_content(),
            "background": True,
            "tools": tools,
            **kwargs,
        }

        api_response, _api_calls = await self._execute_with_retry(parameters, configuration_name)

        result, usage = self._process_response(api_response)

        elapsed = time.time() - start_time
        Logger().info(f"Deep research completed in {elapsed / 60:.1f} minutes")

        return result, usage

    def _process_response(self, api_response: Any) -> tuple[dict, Any]:
        result = {
            "output_text": getattr(api_response, "output_text", None),
            "annotations": [],
            "tool_calls": [],
            "status": getattr(api_response, "status", None),
        }

        for output in getattr(api_response, "output", ()):
            output_type = getattr(output, "type", None)

            if output_type == "message":
                for content_item in getattr(output, "content", ()):
                    if hasattr(content_item, "annotations"):
                        result["annotations"].extend(
                            {
                                "url": a.url,
                                "title": a.title,
                                "start_index": a.start_index,
                                "end_index": a.end_index,
                            }
                            for a in content_item.annotations
                            if hasattr(a, "url")
                        )

            elif output_type in ("web_search_call", "file_search_call", "code_interpreter_call", "mcp_tool_call"):
                result["tool_calls"].append(
                    {
                        "type": output_type,
                        "id": getattr(output, "id", None),
                        "status": getattr(output, "status", None),
                        "action": getattr(output, "action", None),
                    }
                )

        return result, getattr(api_response, "usage", None)

    async def _create_api_call(self, parameters: dict) -> tuple[Any, int]:
        response = await self.client.responses.create(**parameters)

        while response.status in ("queued", "in_progress"):
            await asyncio.sleep(5)
            response = await self.client.responses.retrieve(response.id)

        return response, 1
