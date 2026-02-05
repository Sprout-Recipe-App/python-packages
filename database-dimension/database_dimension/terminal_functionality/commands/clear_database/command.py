import asyncio

from dotenv import find_dotenv, load_dotenv

from ....mongodb.client import get_mongodb_client


def main():
    load_dotenv(find_dotenv(usecwd=True))
    client = get_mongodb_client()
    database_names = asyncio.run(client.list_database_names())
    drops = [client.drop_database(name) for name in database_names if name not in ("admin", "local")]
    if drops:
        asyncio.run(asyncio.wait(drops))
