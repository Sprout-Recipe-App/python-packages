import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from novelty_engine.api_operations.get_ideas import GetIdeas
from novelty_engine.terminal_functionality import terminal_command_registry


@terminal_command_registry.register_command(name="get_ideas")
def get_ideas() -> None:
    cwd = Path.cwd()
    if env := next(
        (p / "Backend" / ".env" for p in (cwd, *cwd.parents) if (p / "Backend" / ".env").exists()), None
    ):
        load_dotenv(env, override=True)
    ideas = asyncio.run(GetIdeas().execute())
    (cwd / "ideas.json").write_text(
        json.dumps([i.model_dump(mode="json", by_alias=True) for i in ideas], indent=2)
    )
