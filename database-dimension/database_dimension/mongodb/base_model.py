from datetime import timezone
from typing import Annotated, ClassVar, Self

from bson import ObjectId
from bson.codec_options import CodecOptions
from pydantic import AliasChoices, BaseModel, BeforeValidator, Field

from .client import get_mongodb_client


class MongoDBBaseModel(BaseModel):
    _codec_options: ClassVar[CodecOptions] = CodecOptions(tz_aware=True, tzinfo=timezone.utc)

    id: Annotated[
        str | None, BeforeValidator(lambda value: str(value) if isinstance(value, ObjectId) else value)
    ] = Field(None, validation_alias=AliasChoices("_id", "id"))

    def __init_subclass__(cls, collection=None, database=None, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in [("_collection_name", collection), ("_database_name", database)]:
            if value:
                setattr(cls, attr, value)

    def to_document(self):
        return self.model_dump(mode="python", exclude_none=True, exclude={"id"})

    @classmethod
    def collection(cls):
        return get_mongodb_client()[cls._database_name].get_collection(
            cls._collection_name, codec_options=cls._codec_options
        )

    @classmethod
    async def find_one(cls, query=None) -> Self | None:
        query = {"_id": query} if isinstance(query, str) else (query or {})
        return cls.model_validate(document) if (document := await cls.collection().find_one(query)) else None

    @classmethod
    async def find(cls, query=None, sort=None, limit=0) -> list[Self]:
        return [
            cls.model_validate(document)
            async for document in cls.collection().find(query or {}, sort=sort, limit=limit)
        ]

    async def save(self):
        self.id = self.id or str(ObjectId())
        await type(self).collection().replace_one({"_id": self.id}, self.to_document(), upsert=True)
        return self.id

    @staticmethod
    def _collection_operation(name):
        async def operation(cls, query, *args, **kwargs):
            return await getattr(cls.collection(), name)(query, *args, **kwargs)

        return classmethod(operation)

    update_one = _collection_operation.__func__("update_one")
    update_many = _collection_operation.__func__("update_many")
    delete_one = _collection_operation.__func__("delete_one")
    delete_many = _collection_operation.__func__("delete_many")
