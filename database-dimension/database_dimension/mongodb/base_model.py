from bson import ObjectId
from bson.decimal128 import Decimal128
from pydantic import BaseModel, Field, create_model, model_validator


class MongoDBBaseModel(BaseModel):
    id: str | None = Field(default=None, json_schema_extra={"llm_exclude": True})

    @classmethod
    def llm_schema(cls):
        return create_model(
            f"{cls.__name__}LLMSchema",
            **{
                n: (i.annotation, i)
                for n, i in cls.model_fields.items()
                if not (i.json_schema_extra or {}).get("llm_exclude")
            },
        )

    @model_validator(mode="before")
    @classmethod
    def _convert_mongodb_types(cls, data):
        def convert(v):
            match v:
                case BaseModel():
                    return convert(v.model_dump())
                case Decimal128():
                    return v.to_decimal()
                case ObjectId():
                    return str(v)
                case dict():
                    return {("id" if k == "_id" else k): convert(n) for k, n in v.items()}
                case list():
                    return [convert(i) for i in v]
                case _:
                    return v

        return convert(data)

    def to_mongodb_dictionary(self):
        data = self.model_dump(mode="json", exclude_none=True, exclude={"id"})
        if self.id:
            data["_id"] = ObjectId(self.id) if ObjectId.is_valid(self.id) else self.id
        return data
