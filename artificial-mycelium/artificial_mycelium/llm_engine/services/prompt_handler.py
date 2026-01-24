import json
from pathlib import Path
import re
from typing import Any

from pydantic import TypeAdapter
import yaml


class PromptHandler:
    _PLACEHOLDER_PATTERN = re.compile(r"<<(\w+)>>")

    @classmethod
    def _fill_placeholders(cls, text: str, mapping: dict) -> str:
        return cls._PLACEHOLDER_PATTERN.sub(lambda match: str(mapping.get(match.group(1), match.group(0))), text)

    @classmethod
    def build_prompt(cls, prompt_location: tuple, placeholder_values: dict = None) -> str:
        values = placeholder_values or {}
        config = yaml.safe_load(Path(prompt_location[0]).with_name("prompts.yaml").read_text())[prompt_location[1]]

        instructions = [
            f"- {cls._fill_placeholders(text, values)}"
            for item in config.get("instructions", [])
            if item
            and (
                text := f"{next(iter(item))}: {item[next(iter(item))] or ''}"
                if isinstance(item, dict)
                else str(item)
            )
            and all(values.get(token) for token in cls._PLACEHOLDER_PATTERN.findall(text))
        ]
        raw_input = config.get("input")
        inputs = [
            filled
            for template in ([raw_input] if not isinstance(raw_input, list) else raw_input)
            if template
            and not cls._PLACEHOLDER_PATTERN.search(filled := cls._fill_placeholders(str(template), values))
        ]

        parts = [f"{'\n\n'.join(inputs).rstrip()}\n"] if inputs else []
        if instructions:
            parts.extend(["[INSTRUCTIONS FOR YOU TO FOLLOW]", *instructions])
        return "\n".join(parts)

    @classmethod
    def _build_schema_example(
        cls, schema: dict, definitions: dict = None, optional: bool = False
    ) -> dict | list | str:
        definitions = definitions or schema.get("$defs", {})
        if "$ref" in schema:
            return cls._build_schema_example(definitions[schema["$ref"].split("/")[-1]], definitions, optional)
        if combiner := next((key for key in ("allOf", "anyOf") if key in schema), None):
            options = schema[combiner]
            enum_values = [value for option in options if "enum" in option for value in option["enum"]]
            other_types = [option.get("type") for option in options if "type" in option and "enum" not in option]
            if enum_values or other_types:
                result = f"<one of: {', '.join([f'{repr(v)}' for v in enum_values] + other_types)}>"
                return f"{schema.get('description', '')} {result}".strip() if schema.get("description") else result
            result = cls._build_schema_example(options[0], definitions, optional)
            return schema.get("description", result) if isinstance(result, str) else result

        description, type_name = schema.get("description"), schema.get("type")
        prefix = "(optional) " if optional else ""

        if "enum" in schema:
            enum_string = f"<one of: {', '.join(str(value) for value in schema['enum'])}>"
            return f"{prefix}{description} {enum_string}" if description else f"{prefix}{enum_string}"
        if type_name == "array":
            item = cls._build_schema_example(schema.get("items", {}), definitions)
            return [f"{description} {item}"] if description and isinstance(item, str) else [item]
        if type_name == "object" or "properties" in schema:
            required = set(schema.get("required", []))
            return {
                k: cls._build_schema_example(v, definitions, optional=k not in required)
                for k, v in schema.get("properties", {}).items()
            }

        type_string = f"optional {type_name}" if optional and type_name else type_name
        return " ".join(filter(None, [description, f"<{type_string}>" if type_string else None])) or "..."

    @classmethod
    def build_prompt_with_schema(cls, prompt: str, response_format: Any = None) -> str:
        if hasattr(response_format, "model_json_schema"):
            schema = response_format.model_json_schema()
        else:
            try:
                schema = TypeAdapter(response_format).json_schema()
            except Exception:
                schema = None
        if not schema:
            return prompt
        return f"{prompt}\n\nRespond with JSON matching this structure (omit optional keys if not needed):\n{json.dumps(cls._build_schema_example(schema), indent=2)}"
