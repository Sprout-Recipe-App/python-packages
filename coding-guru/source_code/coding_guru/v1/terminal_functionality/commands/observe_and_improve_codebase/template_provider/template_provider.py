from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path


class TemplateProvider(ABC):
    def __init__(self, created_path: Path) -> None:
        self.created_path = created_path

    @property
    @abstractmethod
    def DEFAULT_FILE_TEMPLATE_PATH(self) -> Path: ...

    @property
    @abstractmethod
    def FILE_TEMPLATES_DIRECTORY(self) -> Path: ...

    @property
    @abstractmethod
    def DIRECTORY_TEMPLATES_DIRECTORY(self) -> Path: ...

    @property
    @abstractmethod
    def _PATTERNS_FOR_TEMPLATE_FILE_PATHS(self) -> dict[Path, dict[str, list[str]]]: ...

    @property
    @abstractmethod
    def _PATTERNS_FOR_TEMPLATE_DIRECTORY_PATHS(self) -> dict[Path, dict[str, list[str]]]: ...

    @staticmethod
    @abstractmethod
    def get_replacements_for_created_path(created_path: Path, template_path_stem: str) -> dict[str, str]: ...

    @staticmethod
    @abstractmethod
    def extract_parts_of_path_name(name: str) -> list[str]: ...

    @staticmethod
    def should_process_path(path: Path) -> bool:
        return (path.is_file() and not path.stat().st_size) or (path.is_dir() and not any(path.iterdir()))

    @staticmethod
    def build_parent_patterns(base_directory_name: str, max_levels: int) -> list[str]:
        return [f"{base_directory_name}{'/' * level}" for level in range(1, max_levels + 1)]

    def _check_parent_patterns(self, patterns_for_template_paths: dict[Path, dict[str, list[str]]]) -> Path | None:
        for template_path, patterns in patterns_for_template_paths.items():
            for levels_up, parent_directory in enumerate(self.created_path.parents, 1):
                if any(
                    (t := p.rstrip("/")) == parent_directory.name and len(p) - len(t) == levels_up
                    for p in patterns.get("parent_patterns", [])
                ):
                    return template_path

    def _check_name_patterns(
        self, patterns_for_template_paths: dict[Path, dict[str, list[str]]], name: str
    ) -> Path | None:
        parts = self.extract_parts_of_path_name(name)
        for template_path, patterns in patterns_for_template_paths.items():
            if any(
                self.parts_match_in_order(parts, self.extract_parts_of_path_name(p))
                for p in patterns.get("name_patterns", [])
            ):
                return template_path

    def get_template_path_for_added_file(self) -> Path:
        return (
            self._check_name_patterns(self._PATTERNS_FOR_TEMPLATE_FILE_PATHS, self.created_path.stem)
            or self._check_parent_patterns(self._PATTERNS_FOR_TEMPLATE_FILE_PATHS)
            or self.DEFAULT_FILE_TEMPLATE_PATH
        )

    def get_template_path_for_added_directory(self) -> Path | None:
        return self._check_name_patterns(
            self._PATTERNS_FOR_TEMPLATE_DIRECTORY_PATHS, self.created_path.name
        ) or self._check_parent_patterns(self._PATTERNS_FOR_TEMPLATE_DIRECTORY_PATHS)

    @staticmethod
    def get_provider(created_path: Path) -> TemplateProvider | None:
        template_type = (
            created_path.suffix[1:]
            if created_path.is_file()
            else ("swift" if created_path.name[0].isupper() else "py")
        )
        if not (
            target := {
                "py": ("python_template_provider", "PythonTemplateProvider"),
                "swift": ("swift_template_provider", "SwiftTemplateProvider"),
            }.get(template_type)
        ):
            return None
        module_name, class_name = target
        return getattr(import_module(f"{__package__}.implementations.{module_name}"), class_name)(created_path)

    @staticmethod
    def get_template_path(created_path: Path) -> Path:
        if not (provider := TemplateProvider.get_provider(created_path)):
            raise ValueError(f"No template provider available for file: {created_path}")
        return provider.get_template_path_for_added_file()

    @staticmethod
    def parts_match_in_order(sequence_parts: list[str], pattern_parts: list[str]) -> bool:
        pattern_index = 0
        for current_part in sequence_parts:
            if pattern_index < len(pattern_parts) and current_part == pattern_parts[pattern_index]:
                pattern_index += 1
        return pattern_index == len(pattern_parts)
