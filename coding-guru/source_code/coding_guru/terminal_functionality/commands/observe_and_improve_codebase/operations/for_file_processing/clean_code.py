from pathlib import Path
import re

from dev_pytopia import Logger, Operation
from dev_pytopia.terminal_functionality.commands.execute_and_restart_program.program_restarter.program_restarter import (
    ProgramRestarter,
)

PROCESSING_MARKER = "THIS FILE IS BEING PROCESSED"
PROCESSED_MARKER = "THIS CODE HAS BEEN PROCESSED!"
ORIGINAL_CODE_MARKER = "ORIGINAL CODE BEFORE PROCESSING"
COMMENT_STYLES = {
    "swift": {"line_comment": "//"},
    "python": {"line_comment": "#"},
}
DEFAULT_COMMENT_STYLE = COMMENT_STYLES["python"]
logger = Logger(log_level="INFO")


def is_formatted_marker_line(line: str) -> bool:
    """Check if a line is a formatted marker line with equals signs."""
    return "=" in line and any(
        marker in line for marker in [PROCESSING_MARKER, PROCESSED_MARKER, ORIGINAL_CODE_MARKER]
    )


class CleanCode(Operation):
    def __init__(
        self,
        file_path: Path,
        save_to_file: bool = True,
        remove_markers: bool = True,
        remove_organization_marker: bool = True,
    ) -> None:
        self.file_path = self.target_file_path = file_path
        self.should_save_to_file = save_to_file
        self.should_remove_markers = remove_markers
        self.should_remove_organization_marker = remove_organization_marker
        self.language = "swift" if file_path.suffix.lstrip(".").lower() == "swift" else "python"
        self.line_comment = COMMENT_STYLES.get(self.language, DEFAULT_COMMENT_STYLE)["line_comment"]

    async def execute(self):
        async with ProgramRestarter.restarter_lock():
            with open(self.target_file_path, "r") as f:
                content = f.read()

        if content and self.should_remove_markers and self.should_remove_organization_marker:
            lines = content.splitlines()
            cleaned_lines = []
            skip_remaining_lines = False

            for line in lines:
                if skip_remaining_lines:
                    continue

                stripped_line = line.strip()

                if is_formatted_marker_line(stripped_line) or stripped_line in [
                    f"{self.line_comment} {PROCESSED_MARKER}",
                    f"{self.line_comment} {PROCESSING_MARKER}",
                ]:
                    if ORIGINAL_CODE_MARKER in stripped_line:
                        skip_remaining_lines = True
                    continue

                if self.language == "swift" and stripped_line == "//":
                    continue

                cleaned_lines.append(line)

            content = "\n".join(cleaned_lines).strip()

        if self.should_save_to_file:
            with open(self.target_file_path, "w") as f:
                f.write(content)
            return ""
        return content

    @staticmethod
    def clean_escaped_quotes_in_swift_strings(code: str) -> str:
        return re.sub(
            r'"((?:[^"\\]|\\.|"\((?:[^()]|\([^()]*\))*\)")*)"',
            lambda m: f'"{re.sub(r'\\"', '"', m.group(1))}"',
            code,
        )

    @classmethod
    def should_process_path(cls, path: Path) -> bool:
        return True
