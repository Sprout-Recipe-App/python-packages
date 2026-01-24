from pathlib import Path

import yaml


class InstructionManager:
    _instances: dict[Path, "InstructionManager"] = {}
    _instructions_file_path: Path
    _config: dict

    def __new__(cls, config_path: Path):
        if (abs_config_path := config_path.resolve()) not in cls._instances:
            instance = super().__new__(cls)
            instance._instructions_file_path = abs_config_path
            instance._config = {}
            instance._load_config()
            cls._instances[abs_config_path] = instance
        return cls._instances[abs_config_path]

    def get_instructions(self, file_suffix: str, template_name: str) -> str:
        suffix = file_suffix.lower()
        language_key = "python" if suffix in ("py", "python") else suffix
        universal = self._config.get("universal_instructions", "")
        lang_specific = self._config.get(f"{language_key}_instructions", "")
        language_config = self._config.get(language_key, {})
        template_instructions = next(
            (
                tmpl.get("instructions", "")
                for tmpl_type in ("file_templates", "directory_templates")
                for name, tmpl in language_config.get(tmpl_type, {}).items()
                if name == template_name and tmpl.get("instructions")
            ),
            "",
        )
        sections = (
            f"--- Universal Instructions ---\n{universal}" if universal else None,
            f"--- Language-Specific Instructions ---\n{lang_specific}" if lang_specific else None,
            f"--- Template-Specific Instructions ---\n{template_instructions}" if template_instructions else None,
        )
        return "\n\n".join(filter(None, sections))

    def _load_config(self) -> None:
        try:
            with open(self._instructions_file_path) as f:
                self._config = yaml.safe_load(f) or {}
        except Exception:
            self._config = {}
