import asyncio

from dotenv import find_dotenv, load_dotenv

from ....mongodb.client import get_mongodb_client


def main():
    load_dotenv(find_dotenv(usecwd=True))

    async def clear():
        client = get_mongodb_client()
        protected = {"admin", "config", "local"}
        await asyncio.gather(
            *(client.drop_database(name) for name in await client.list_database_names() if name not in protected)
        )

    asyncio.run(clear())
