import importlib
import inspect
from pathlib import Path

import click


def create_terminal_entrypoint():
    module = inspect.getmodule(inspect.currentframe().f_back)
    root, pkg = Path(module.__file__).parent, module.__package__
    group = click.Group(pkg.split(".")[0])

    def main():
        for p in (root / "commands").glob("*/command.py"):
            mod = importlib.import_module(f"{pkg}.commands.{p.parent.name}.command")
            group.add_command(
                click.command(p.parent.name.replace("_", "-"), **getattr(mod, "COMMAND_SETTINGS", {}))(mod.main)
            )
        group()

    return main
