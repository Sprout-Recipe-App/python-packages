from typing import Any

from pydantic import TypeAdapter


def get_json_schema(fmt: Any) -> dict | None:
    try:
        return TypeAdapter(fmt).json_schema()
    except Exception:
        return None
