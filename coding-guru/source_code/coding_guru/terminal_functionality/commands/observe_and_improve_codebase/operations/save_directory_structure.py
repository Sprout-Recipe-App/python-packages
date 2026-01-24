from contextlib import suppress
from datetime import datetime
import json
from pathlib import Path

import aiofiles

from dev_pytopia import Operation


class SaveDirectoryStructure(Operation):
    DEFAULT_EXCLUDED_ITEMS = {".pytest_cache", ".ruff_cache", ".venv", "lib", "__pycache__"}

    def _find_path_up_to_boundary(self, start_path: Path, target_name: str, boundary_path: Path | None = None):
        cur = (start_path if start_path.is_dir() else start_path.parent).resolve()
        b = boundary_path and boundary_path.resolve()
        while cur not in (b, cur.parent):
            if (t := cur / target_name).exists():
                return t
            with suppress(PermissionError, OSError):
                for d in (p for p in cur.iterdir() if p.is_dir()):
                    if (t := d / target_name).exists():
                        return t
            cur = cur.parent

    def __init__(self, path: Path, addtional_items_to_exclude: set[str] | None = None):
        super().__init__()
        self._should_proceed = False
        if not (cfg_path := self._find_path_up_to_boundary(path, "coding-guru-configuration.json")):
            return
        if not isinstance(cfg := json.loads(cfg_path.read_text()), dict):
            return
        if not isinstance(dcfg := cfg.get("directory_structure_generation"), dict):
            return
        self.config_directory = cfg_path.parent
        if not (out := dcfg.get("output_path")):
            return
        self.output_file_path = (self.config_directory / out).resolve()
        self.directory_to_examine_structure_of = self.config_directory / dcfg.get("directory_to_examine", ".")
        self.directory_to_examine_structure_of = self.directory_to_examine_structure_of.resolve()
        self.excluded_items = (
            self.DEFAULT_EXCLUDED_ITEMS
            | set(dcfg.get("excluded_items", []))
            | (addtional_items_to_exclude or set())
        )
        self._should_proceed = True

    async def execute(self):
        if not self._should_proceed:
            return
        p = self.output_file_path
        p.parent.mkdir(parents=True, exist_ok=True)
        new = self._generate_file_content()
        with suppress(FileNotFoundError):
            async with aiofiles.open(p, encoding="utf-8") as f:
                if new == await f.read():
                    return
        async with aiofiles.open(p, "w", encoding="utf-8") as f:
            await f.write(new)

    def _generate_file_content(self) -> str:
        return f"Directory structure in: {self.directory_to_examine_structure_of}\nGenerated on {datetime.now():%B %d, %Y at %I:%M:%S %p %Z}\n\n{self._generate_directory_structure(self.directory_to_examine_structure_of)}"

    def _generate_directory_structure(self, root: Path) -> str:
        def walk(p: Path, depth: int = 0):
            indent = "    " * depth
            for e in sorted(p.iterdir()):
                if self._is_excluded_item(e):
                    continue
                if e.is_dir():
                    yield f"{indent}[{e.name}/]"
                    yield from walk(e, depth + 1)
                else:
                    yield f"{indent}- {e.name}"

        return "\n".join(walk(root)) + "\n"

    def _is_excluded_item(self, path: Path) -> bool:
        return any(part in self.excluded_items for part in path.parts)
