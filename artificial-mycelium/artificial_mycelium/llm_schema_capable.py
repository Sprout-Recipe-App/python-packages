from pydantic import create_model


class LLMSchemaCapable:
    @classmethod
    def llm_schema(cls):
        return create_model(
            f"{cls.__name__}LLMSchema",
            **{
                field_name: (field_info.annotation, field_info)
                for field_name, field_info in cls.model_fields.items()
                if not (field_info.json_schema_extra or {}).get("llm_exclude")
            },
        )
