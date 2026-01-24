from asyncio import gather
from pathlib import Path
import shutil

import aiofiles

from dev_pytopia import Operation


class SetupPythonPackage(Operation):
    def __init__(self, package_name: str):
        super().__init__()
        self.package_name = package_name
        self.source_name = package_name.replace("-", "_")
        self.display_name = package_name.replace("-", " ").title()

    def _find_my_packages_directory(self, path: Path) -> Path:
        return (
            next((p for p in path.parents if p.name == "My Packages"), None)
            or next((p for p in path.parents if p.name == "Useful Python Things"), None) / "My Packages"
            or Path.cwd() / "Useful Python Things" / "My Packages"
        )

    async def _replace_placeholders(self, file_path: Path) -> None:
        if not file_path.is_file() or b"\0" in open(file_path, "rb").read(1024):
            return

        async with aiofiles.open(file_path) as f:
            content = await f.read()

        for old, new in (
            ("<package_name>", self.source_name),
            ("<package-name>", self.package_name),
            ("<Package Name>", self.display_name),
        ):
            content = content.replace(old, new)

        async with aiofiles.open(file_path, "w") as f:
            await f.write(content)

    async def execute(self):
        my_packages_dir = self._find_my_packages_directory(Path(__file__))
        my_packages_dir.mkdir(parents=True, exist_ok=True)

        project_dir = my_packages_dir / self.display_name
        shutil.copytree(
            Path(__file__).parents[1] / "templates/python_package_template", project_dir, dirs_exist_ok=True
        )
        shutil.move(project_dir / "source_code/package_name", project_dir / f"source_code/{self.source_name}")

        await gather(*(self._replace_placeholders(p) for p in project_dir.rglob("*")))

        return str(project_dir)
