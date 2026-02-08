from typing import get_args, get_origin

from pydantic import BaseModel, create_model


class LLMSchemaCapable:
    @classmethod
    def llm_schema(cls):
        def f(t):
            if get_origin(t) is list and (a := get_args(t)):
                return list[f(a[0])]
            if isinstance(t, type) and issubclass(t, BaseModel):
                fields = {
                    n: (f(i.annotation), i)
                    for n, i in t.model_fields.items()
                    if n != "id" and not (i.json_schema_extra or {}).get("llm_exclude")
                }
                return create_model(f"{t.__name__}LLM", **fields)
            return t

        return f(cls)
