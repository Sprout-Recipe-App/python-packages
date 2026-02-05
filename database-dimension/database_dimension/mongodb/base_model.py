from datetime import timezone
from typing import Annotated, Self

from bson import ObjectId
from bson.codec_options import CodecOptions
from pydantic import AliasChoices, BaseModel, BeforeValidator, Field

from .client import get_mongodb_client

_CODEC_OPTIONS = CodecOptions(tz_aware=True, tzinfo=timezone.utc)


class MongoDBBaseModel(BaseModel):
    id: Annotated[
        str | None, BeforeValidator(lambda value: str(value) if isinstance(value, ObjectId) else value)
    ] = Field(None, validation_alias=AliasChoices("_id", "id"), json_schema_extra={"llm_exclude": True})

    def __init_subclass__(cls, collection: str = None, database: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._collection_name, cls._database_name = collection, database

    @staticmethod
    def _collection_operation_method(operation_name: str, *, keyword_map: dict[str, str] | None = None):
        async def operation(cls, query: dict, *args, **kwargs):
            if keyword_map:
                kwargs = {keyword_map.get(key, key): value for key, value in kwargs.items()}
            return await getattr(cls.collection(), operation_name)(cls._normalize_query(query), *args, **kwargs)

        return classmethod(operation)

    @classmethod
    def collection(cls):
        return get_mongodb_client()[cls._database_name].get_collection(
            cls._collection_name, codec_options=_CODEC_OPTIONS
        )

    @classmethod
    def _to_object_id(cls, id_value):
        return ObjectId(id_value) if isinstance(id_value, str) and ObjectId.is_valid(id_value) else id_value

    @classmethod
    def _normalize_query(cls, query: dict | None = None) -> dict:
        return {**query, "_id": cls._to_object_id(query["_id"])} if query and "_id" in query else query or {}

    @classmethod
    async def find_one(cls, query: dict | None = None) -> Self | None:
        return next(iter(await cls.find(query, limit=1)), None)

    @classmethod
    async def find_by_ids(cls, ids: list[str]) -> list[Self]:
        return [] if not ids else await cls.find({"_id": {"$in": [*map(cls._to_object_id, ids)]}})

    @classmethod
    async def find(
        cls,
        query: dict | None = None,
        sort: list | None = None,
        limit: int | None = None,
    ) -> list[Self]:
        cursor = cls.collection().find(cls._normalize_query(query), sort=sort or None, limit=limit or 0)
        return [cls.model_validate(document) async for document in cursor]

    @classmethod
    async def insert_one(cls, data: Self) -> str:
        return str(
            (
                await cls.collection().insert_one(data.model_dump(mode="json", exclude_none=True, exclude={"id"}))
            ).inserted_id
        )

    update_one = _collection_operation_method("update_one", keyword_map={"updates": "update"})
    update_many = _collection_operation_method("update_many", keyword_map={"updates": "update"})
    delete_one = _collection_operation_method("delete_one")
    delete_many = _collection_operation_method("delete_many")

    @classmethod
    async def replace_one(cls, query: dict, replacement: Self, upsert: bool = False):
        return await cls.collection().replace_one(
            cls._normalize_query(query),
            replacement.model_dump(mode="json", exclude_none=True, exclude={"id"}),
            upsert=upsert,
        )
