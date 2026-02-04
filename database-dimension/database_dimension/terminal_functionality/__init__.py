import asyncio

import click
from dotenv import find_dotenv, load_dotenv

from ..mongodb.gateway import DatabaseGateway


@click.group()
def main():
    pass


@main.command()
def reset_database():
    """Drop all non-system databases."""
    load_dotenv(find_dotenv(usecwd=True))

    async def reset():
        client = DatabaseGateway.get()._client
        await asyncio.gather(
            *[client.drop_database(n) for n in await client.list_database_names() if n not in ("admin", "local")]
        )

    asyncio.run(reset())
