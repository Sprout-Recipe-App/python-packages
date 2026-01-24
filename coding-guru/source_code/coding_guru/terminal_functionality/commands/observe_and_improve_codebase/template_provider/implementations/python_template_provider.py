from pathlib import Path

from ..template_provider import TemplateProvider


class PythonTemplateProvider(TemplateProvider):
    _TEMPLATES_DIRECTORY = Path(__file__).parent.parent / "templates/python_templates"

    @staticmethod
    def snake_case_to_pascal_case(snake_case_string: str) -> str:
        return "".join(part.title() for part in snake_case_string.split("_"))

    @property
    def FILE_TEMPLATES_DIRECTORY(self) -> Path:
        return self._TEMPLATES_DIRECTORY / "python_file_templates"

    @property
    def DIRECTORY_TEMPLATES_DIRECTORY(self) -> Path:
        return self._TEMPLATES_DIRECTORY / "python_directory_templates"

    @property
    def _PATTERNS_FOR_FILE_TEMPLATE_FILE_NAMES(self) -> dict[str, dict[str, list[str]]]:
        return {
            "data_handler.md": {"name_patterns": ["data_handler"]},
            "data_model.md": {"parent_patterns": TemplateProvider.build_parent_patterns("data_models", 6)},
            "data_model_handler.md": {"parent_patterns": ["data_model_handlers/"]},
            "api_operation.md": {"parent_patterns": TemplateProvider.build_parent_patterns("api_operations", 3)},
            "operation.md": {"parent_patterns": TemplateProvider.build_parent_patterns("operations", 3)},
            "__init__.md": {"name_patterns": ["__init__"]},
            "__main__.md": {"name_patterns": ["__main__"]},
        }

    _PATTERNS_FOR_DIRECTORY_TEMPLATE_FILE_NAMES = {
        "terminal_functionality.yaml": {"name_patterns": ["terminal_functionality"]},
    }

    @property
    def DEFAULT_FILE_TEMPLATE_PATH(self) -> Path:
        return self.FILE_TEMPLATES_DIRECTORY / "default_file_template.md"

    @property
    def _PATTERNS_FOR_TEMPLATE_FILE_PATHS(self) -> dict[Path, dict[str, list[str]]]:
        d = self.FILE_TEMPLATES_DIRECTORY
        return {d / n: p for n, p in self._PATTERNS_FOR_FILE_TEMPLATE_FILE_NAMES.items()}

    @property
    def _PATTERNS_FOR_TEMPLATE_DIRECTORY_PATHS(self) -> dict[Path, dict[str, list[str]]]:
        d = self.DIRECTORY_TEMPLATES_DIRECTORY
        return {d / n: p for n, p in self._PATTERNS_FOR_DIRECTORY_TEMPLATE_FILE_NAMES.items()}

    @staticmethod
    def get_replacements_for_created_path(created_path: Path, template_path_stem: str) -> dict[str, str]:
        to_pascal = PythonTemplateProvider.snake_case_to_pascal_case
        created_stem = created_path.stem
        stem_without_template = created_stem.replace(template_path_stem, "")
        return {
            "<<<created_path_name>>>": created_path.name,
            "<<<CreatedPathStem>>>": to_pascal(created_stem),
            "<<<created_path_stem_without_template_name>>>": stem_without_template,
            "<<<CreatedPathStemWithoutTemplateName>>>": to_pascal(stem_without_template),
            "<<<parent_of_created_path_name>>>": created_path.parent.name,
        }

    @staticmethod
    def extract_parts_of_path_name(name: str) -> list[str]:
        return [p for p in name.split("_") if p]
