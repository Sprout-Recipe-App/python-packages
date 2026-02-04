from typing import Annotated, Self

from bson import ObjectId
from pydantic import AliasChoices, BaseModel, BeforeValidator, Field

from .gateway import DatabaseGateway


class MongoDBBaseModel(BaseModel):
    id: Annotated[str | None, BeforeValidator(lambda v: str(v) if isinstance(v, ObjectId) else v)] = Field(
        None, validation_alias=AliasChoices("_id", "id"), json_schema_extra={"llm_exclude": True}
    )

    def __init_subclass__(cls, collection: str = None, db: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._collection_name, cls._db_name = collection, db

    def to_mongodb_dictionary(self):
        return self.model_dump(mode="json", exclude_none=True, exclude={"id"})

    @classmethod
    def collection(cls):
        return DatabaseGateway.get().get_collection(cls)

    @classmethod
    def _to_object_id(cls, id_value):
        return (
            ObjectId(id_value) if ObjectId.is_valid(id_value) and not isinstance(id_value, ObjectId) else id_value
        )

    @classmethod
    def _normalize_query(cls, query: dict) -> dict:
        return {**query, "_id": cls._to_object_id(query["_id"])} if "_id" in query else query

    @classmethod
    async def find_one(cls, query: dict) -> Self | None:
        if doc := await cls.collection().find_one(cls._normalize_query(query)):
            return cls.model_validate(doc)
        return None

    @classmethod
    async def load_by_id(cls, id_value: str) -> Self | None:
        return await cls.find_one({"_id": id_value})

    @classmethod
    async def load_by_ids(cls, ids: list[str]) -> list[Self]:
        if not ids:
            return []
        cursor = cls.collection().find({"_id": {"$in": [cls._to_object_id(i) for i in ids]}})
        return [cls.model_validate(doc) async for doc in cursor]

    @classmethod
    async def load(
        cls,
        query: dict | None = None,
        sort: list | None = None,
        limit: int | None = None,
        projection: dict | None = None,
    ) -> list[Self]:
        cursor = cls.collection().find(cls._normalize_query(query or {}), projection)
        cursor = cursor.sort(sort) if sort else cursor
        cursor = cursor.limit(limit) if limit else cursor
        return [cls.model_validate(doc) async for doc in cursor]

    @classmethod
    async def load_latest(cls, query: dict | None = None) -> Self | None:
        if doc := await cls.collection().find_one(cls._normalize_query(query or {}), sort=[("_id", -1)]):
            return cls.model_validate(doc)
        return None

    @classmethod
    async def insert_one(cls, data: Self) -> str:
        result = await cls.collection().insert_one(data.to_mongodb_dictionary())
        return str(result.inserted_id)

    @classmethod
    async def update_one(cls, query: dict, updates: dict, upsert: bool = False):
        return await cls.collection().update_one(cls._normalize_query(query), updates, upsert=upsert)

    @classmethod
    async def update_many(cls, query: dict, updates: dict, array_filters: list | None = None):
        options = {"array_filters": array_filters} if array_filters else {}
        return await cls.collection().update_many(cls._normalize_query(query), updates, **options)

    @classmethod
    async def replace_one(cls, query: dict, replacement: Self, upsert: bool = False):
        return await cls.collection().replace_one(
            cls._normalize_query(query), replacement.to_mongodb_dictionary(), upsert=upsert
        )

    @classmethod
    async def delete_one(cls, query: dict):
        return await cls.collection().delete_one(cls._normalize_query(query))

    @classmethod
    async def delete_many(cls, query: dict):
        return await cls.collection().delete_many(cls._normalize_query(query))
