from pathlib import Path
import re

from ..template_provider import TemplateProvider


class SwiftTemplateProvider(TemplateProvider):
    _TEMPLATES_DIRECTORY = Path(__file__).parent.parent / "templates/swift_templates"

    @staticmethod
    def pascal_case_to_kebab_case(pascal_case_string: str) -> str:
        return "-".join(word.lower() for word in re.findall(r"[A-Z][a-z0-9]*", pascal_case_string))

    @property
    def FILE_TEMPLATES_DIRECTORY(self) -> Path:
        return self._TEMPLATES_DIRECTORY / "swift_file_templates"

    @property
    def DIRECTORY_TEMPLATES_DIRECTORY(self) -> Path:
        return self._TEMPLATES_DIRECTORY / "swift_directory_templates"

    @property
    def _PATTERNS_FOR_FILE_TEMPLATE_FILE_NAMES(self) -> dict[str, dict[str, list[str]]]:
        bp = TemplateProvider.build_parent_patterns
        return {
            "DefaultFileTemplate.md": {"name_patterns": ["DefaultFileTemplate"]},
            "DataModel.md": {"parent_patterns": bp("DataModels", 3)},
            "StateHandler.md": {"name_patterns": ["StateHandler"]},
            "Page.md": {"name_patterns": ["Page"]},
            "PageContext.md": {"name_patterns": ["PageContext"]},
            "PageOperations.md": {"name_patterns": ["PageOperations"]},
            "View.md": {
                "name_patterns": ["View"],
                "parent_patterns": bp("Views", 2) + bp("SharedViews", 1),
            },
            "Styles.md": {"name_patterns": ["Styles"]},
            "Subview.md": {"parent_patterns": bp("Subviews", 2)},
            "APIOperation.md": {"parent_patterns": bp("APIOperations", 1)},
        }

    @property
    def _PATTERNS_FOR_DIRECTORY_TEMPLATE_FILE_NAMES(self) -> dict[str, dict[str, list[str]]]:
        bp = TemplateProvider.build_parent_patterns
        return {
            "page.yaml": {"parent_patterns": bp("Pages", 1)},
            "subview.yaml": {"parent_patterns": bp("Subviews", 1)},
            "view.yaml": {"parent_patterns": bp("Views", 1)},
        }

    @property
    def DEFAULT_FILE_TEMPLATE_PATH(self) -> Path:
        return self.FILE_TEMPLATES_DIRECTORY / "DefaultFileTemplate.md"

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
        created_stem = created_path.stem
        return {
            "<<<CreatedPathName>>>": created_path.name,
            "<<<CreatedPathStem>>>": created_stem,
            "<<<CreatedPathStemWithoutTemplateName>>>": created_stem.replace(template_path_stem, ""),
            "<<<created-path-stem>>>": SwiftTemplateProvider.pascal_case_to_kebab_case(created_stem),
        }

    @staticmethod
    def extract_parts_of_path_name(name: str) -> list[str]:
        return re.findall(r"[A-Z][^A-Z]*", name)
