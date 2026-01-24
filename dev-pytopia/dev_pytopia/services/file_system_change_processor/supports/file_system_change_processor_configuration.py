from dataclasses import dataclass
from pathlib import Path

from pathspec import PathSpec


@dataclass
class FileSystemChangeProcessorConfiguration:
    directories_to_observe: list[str | Path]
    include_globs: tuple[str, ...] = ()
    exclude_globs: tuple[str, ...] = ()
    processing_debounce: int = 500

    _DEFAULT_INCLUDES = ("**/*.py", "**/*.md", "**/*.mdc", "**/*.json", "**/*.yaml", "**/*.yml")
    _DEFAULT_EXCLUDES = ("**/__pycache__/**", "**/.git/**", "**/.pytest_cache/**", "**/.ruff_cache/**")

    def __post_init__(self):
        self.directories_to_observe = list(map(str, self.directories_to_observe))
        self.include_globs = self._normalize(self.include_globs, self._DEFAULT_INCLUDES)
        self.exclude_globs = self._normalize(self.exclude_globs, self._DEFAULT_EXCLUDES)
        self._include_spec = (
            PathSpec.from_lines("gitwildmatch", self.include_globs) if self.include_globs else None
        )
        self._exclude_spec = (
            PathSpec.from_lines("gitwildmatch", self.exclude_globs) if self.exclude_globs else None
        )

    @staticmethod
    def _normalize(value: tuple | list | str, default: tuple[str, ...]) -> tuple[str, ...]:
        items = value if isinstance(value, (list, tuple)) else str(value).split(",")
        return tuple(s for v in items if (s := str(v).strip())) or default
