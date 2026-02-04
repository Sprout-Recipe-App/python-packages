from fast_server import APIOperation

from ..data.idea import Idea


class GetIdeas(APIOperation):
    METHOD = "GET"

    async def execute(self) -> list[Idea]:
        return await Idea.pop_unprocessed()
