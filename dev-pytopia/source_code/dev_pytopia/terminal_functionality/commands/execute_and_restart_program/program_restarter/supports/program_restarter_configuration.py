from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProgramRestarterConfiguration:
    command: list[str]
    directories_to_observe: list[str | Path]
    enable_restart_from_terminal: bool = False
    enable_file_observing: bool = True
    include_globs: list[str] | None = None
    exclude_globs: list[str] | None = None

    def __post_init__(self):
        self.command = self.command.split() if isinstance(self.command, str) else self.command
        self.directories_to_observe = [*map(Path, self.directories_to_observe)]
        if not self.enable_file_observing:
            self.include_globs = self.exclude_globs = []

    @classmethod
    def from_cli(cls, command_and_arguments: tuple[str, ...]):
        root = Path().resolve()
        dirs_to_watch = [src] if (src := root / "source_code").is_dir() else [root]

        return cls(
            command=list(command_and_arguments),
            directories_to_observe=dirs_to_watch,
            enable_restart_from_terminal=True,
            exclude_globs=["**/__pycache__/**", "**/*.pyc"],
        )
