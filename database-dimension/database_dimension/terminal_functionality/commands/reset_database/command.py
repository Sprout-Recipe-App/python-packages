import asyncio
import importlib
from pathlib import Path
import sys

import click
from dotenv import find_dotenv, load_dotenv

from ....terminal_functionality import terminal_command_registry


@terminal_command_registry.register_command(name="reset-database")
@click.option("--source", required=True, type=click.Path(exists=True), help="Path to source code directory")
@click.option("--pattern", default="*_data_model_handler.py", help="Glob pattern for handler files")
def reset_database(source: str, pattern: str):
    source_path = Path(source).resolve()
    load_dotenv(find_dotenv(usecwd=True))

    from ....mongodb.handler import DataModelHandler

    sys.path.insert(0, str(source_path))
    for handler_file in source_path.rglob(pattern):
        importlib.import_module(".".join(handler_file.relative_to(source_path).with_suffix("").parts))

    def all_subclasses(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from all_subclasses(sub)

    handlers = [h for h in all_subclasses(DataModelHandler) if hasattr(h, "DB_NAME") and h.DB_NAME]
    if not handlers:
        return click.echo("No handlers found.")

    async def reset():
        click.echo(f"Clearing {len(handlers)} collection(s)...")
        await asyncio.gather(*[handler.delete_many({}) for handler in handlers])
        for handler in handlers:
            if seed_data := getattr(handler, "SEED_DATA", None):
                click.echo(f"Seeding {handler.__name__}...")
                await handler.insert_many(seed_data)

    asyncio.run(reset())
    click.echo("Done.")
