import importlib
import inspect
from pathlib import Path
from typing import Any, Callable

import click


class TerminalCommandRegistry:
    def __init__(self, package_root: Path | None = None) -> None:
        self.package_root = package_root or self._infer_package_root()
        self.package_name, self.module_package = self._infer_package_info()
        self.command_group = click.Group(self.package_name)

    def _infer_package_root(self) -> Path:
        if (frame := inspect.currentframe()) and (module := inspect.getmodule(frame.f_back.f_back)):
            return Path(module.__file__).parent if module.__file__ else Path.cwd()
        return Path.cwd()

    def _infer_package_info(self) -> tuple[str, str]:
        if (
            (frame := inspect.currentframe())
            and (module := inspect.getmodule(frame.f_back.f_back))
            and module.__package__
        ):
            return module.__package__.split(".")[0], module.__package__
        fallback = self.package_root.parent.name
        return fallback, fallback

    def register_command(self, name: str, **kw: Any) -> Callable:
        def decorator(function: Callable) -> Callable:
            self.command_group.add_command(click.command(name, **kw)(function))
            return function

        return decorator

    def run(self, **kw: Any) -> None:
        for command in (self.package_root / "commands").glob("*/command.py"):
            importlib.import_module(f"{self.module_package}.commands.{command.parent.name}.command")
        self.command_group(prog_name=self.package_name, standalone_mode=True, **kw)
