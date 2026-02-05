from datetime import datetime, timezone

from database_dimension import MongoDBBaseModel
from pydantic import Field


class Idea(MongoDBBaseModel, collection="ideas", database="user_data"):
    content: str
    user_id: str | None = Field(default=None, serialization_alias="userId", validation_alias="userId")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: datetime | None = Field(default=None, exclude=True)

    @classmethod
    async def pop_unprocessed(cls) -> list["Idea"]:
        ideas = await cls.find({"processed_at": None}, sort=[("created_at", -1)])
        if ideas:
            await cls.update_many(
                {"_id": {"$in": [idea.id for idea in ideas]}},
                {"$set": {"processed_at": datetime.now(timezone.utc)}},
            )
        return ideas
