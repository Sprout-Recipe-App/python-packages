from datetime import datetime

from database_dimension import DataModelHandler

from .idea import Idea


class IdeaHandler(DataModelHandler):
    DB_NAME: str = "user_data"
    COLLECTION_NAME: str = "ideas"
    MODEL_TYPE = Idea

    @classmethod
    async def pop_unprocessed(cls) -> list[Idea]:
        ideas = await cls.load({"processed_at": None}, sort=[("created_at", -1)])
        if ideas:
            await cls.update_many(
                {"_id": {"$in": [idea.id for idea in ideas]}}, {"$set": {"processed_at": datetime.now()}}
            )
        return ideas
