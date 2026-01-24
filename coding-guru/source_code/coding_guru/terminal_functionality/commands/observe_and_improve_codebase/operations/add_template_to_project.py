from pathlib import Path

import yaml

from dev_pytopia import Operation

from ..template_provider.template_provider import TemplateProvider


class AddTemplateToProject(Operation):
    def __init__(self, created_path: Path):
        self.created_path = created_path
        self.template_provider = TemplateProvider.get_provider(self.created_path)

    async def execute(self) -> None:
        provider = self.template_provider
        if not (provider and provider.should_process_path(self.created_path)):
            return
        await (self._process_directory if self.created_path.is_dir() else self._process_file)(
            self.created_path, provider
        )

    def _replace_template_placeholders(self, text: str, replacements: dict[str, str]) -> str:
        for template_placeholder, replacement in replacements.items():
            text = text.replace(template_placeholder, replacement)
        return text

    async def _process_file(
        self, created_path: Path, provider: TemplateProvider, specified_template: Path | None = None
    ) -> None:
        template_path = specified_template or provider.get_template_path_for_added_file()
        replacements = provider.get_replacements_for_created_path(created_path, template_path.stem)
        created_path.write_text(self._replace_template_placeholders(template_path.read_text(), replacements))

    async def _process_directory(self, created_path: Path, provider: TemplateProvider) -> None:
        template_path = provider.get_template_path_for_added_directory()
        if template_path and (directory_specification := yaml.safe_load(template_path.read_text())):
            await self._create_directory_structure(
                directory_specification["directory_structure"],
                created_path,
                provider.get_replacements_for_created_path(created_path, template_path.stem),
                provider,
            )

    async def _create_directory_structure(
        self, structure: list[dict], target_path: Path, replacements: dict[str, str], provider: TemplateProvider
    ) -> None:
        for file_system_item in structure:
            if "file" in file_system_item:
                await self._process_file(
                    target_path / self._replace_template_placeholders(file_system_item["file"], replacements),
                    provider,
                    specified_template=provider.FILE_TEMPLATES_DIRECTORY / file_system_item["template"],
                )
            else:
                directory_being_created = target_path / self._replace_template_placeholders(
                    file_system_item["directory"], replacements
                )
                directory_being_created.mkdir(exist_ok=True)
                if structure_of_directory_being_created := file_system_item.get("directory_structure"):
                    await self._create_directory_structure(
                        structure_of_directory_being_created, directory_being_created, replacements, provider
                    )
