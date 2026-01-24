from fast_server import APIOperation

from ..data.idea import Idea
from ..data.idea_data_model_handler import IdeaHandler


class GetIdeas(APIOperation):
    METHOD = "GET"

    async def execute(self) -> list[Idea]:
        return await IdeaHandler.pop_unprocessed()

