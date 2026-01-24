from typing import Generic, TypeVar

from bson import ObjectId

from .client import MongoDBClient

T = TypeVar("T")


class DataModelHandler(Generic[T]):
    DB_NAME: str
    COLLECTION_NAME: str
    MODEL_TYPE: type[T]
    _mongodb_client: MongoDBClient | None = None

    def __init_subclass__(cls, db: str = None, collection: str = None, model: type[T] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if db is not None:
            cls.DB_NAME = db
        if collection is not None:
            cls.COLLECTION_NAME = collection
        if model is not None:
            cls.MODEL_TYPE = model

    @classmethod
    def collection(handler):
        if not (client := DataModelHandler._mongodb_client):
            client = DataModelHandler._mongodb_client = MongoDBClient()
        return client.get_collection(handler.DB_NAME, handler.COLLECTION_NAME)

    @classmethod
    def _validate(handler, document: dict | None) -> T | None:
        return handler.MODEL_TYPE.model_validate(document) if document else None

    @classmethod
    def _normalize_query(handler, query: dict) -> dict:
        if "_id" in query and not isinstance(id := query["_id"], ObjectId):
            return {**query, "_id": ObjectId(id) if ObjectId.is_valid(id) else id}
        return query

    @classmethod
    async def insert_one(handler, data: T) -> str:
        return str((await handler.collection().insert_one(data.to_mongodb_dictionary())).inserted_id)

    @classmethod
    async def insert_many(handler, data: list[T]) -> list[str]:
        result = await handler.collection().insert_many([item.to_mongodb_dictionary() for item in data])
        return [str(id) for id in result.inserted_ids]

    @classmethod
    async def update_one(handler, query: dict, updates: dict, upsert: bool = False):
        return await handler.collection().update_one(handler._normalize_query(query), updates, upsert=upsert)

    @classmethod
    async def find_one(handler, query: dict) -> T | None:
        return handler._validate(await handler.collection().find_one(handler._normalize_query(query)))

    @classmethod
    async def load_by_id(handler, id_value: str) -> T | None:
        return await handler.find_one({"_id": id_value})

    @classmethod
    async def load(
        handler,
        query: dict | None = None,
        sort: list[tuple[str, int]] | None = None,
        limit: int | None = None,
        projection: dict | None = None,
    ) -> list[T]:
        cursor = handler.collection().find(query or {}, projection)
        if sort:
            cursor = cursor.sort(sort)
        if limit:
            cursor = cursor.limit(limit)
        return [handler._validate(document) async for document in cursor]

    @classmethod
    async def load_latest(handler, query: dict | None = None) -> T | None:
        return handler._validate(await handler.collection().find_one(query or {}, sort=[("_id", -1)]))

    @classmethod
    async def update_many(handler, query: dict, updates: dict, array_filters: list | None = None):
        kwargs = {"array_filters": array_filters} if array_filters else {}
        return await handler.collection().update_many(query, updates, **kwargs)

    @classmethod
    async def replace_one(handler, query: dict, replacement: T, upsert: bool = False):
        return await handler.collection().replace_one(
            handler._normalize_query(query), replacement.to_mongodb_dictionary(), upsert=upsert
        )

    @classmethod
    async def find_by_field(handler, field: str, value) -> T | None:
        return await handler.find_one({field: value})

    @classmethod
    async def delete_one(handler, query: dict):
        return await handler.collection().delete_one(handler._normalize_query(query))

    @classmethod
    async def delete_many(handler, query: dict):
        return await handler.collection().delete_many(query)
