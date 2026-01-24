from fast_server import APIOperation, get_user_id
from fastapi import Depends

from ..data.idea import Idea
from ..data.idea_data_model_handler import IdeaHandler


class SaveIdea(APIOperation):
    METHOD = "POST"

    async def execute(self, idea: Idea, user_id: str = Depends(get_user_id)):
        idea.user_id = user_id
        await IdeaHandler.insert_one(idea)

