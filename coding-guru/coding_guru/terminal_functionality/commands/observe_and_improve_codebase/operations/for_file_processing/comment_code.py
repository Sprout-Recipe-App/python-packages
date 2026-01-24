"""
╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        Documentation for comment_code.py                                        ║
╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# Standard Library Imports
from pathlib import Path
import re

# Third-Party Imports
# Local Development Imports
from dev_pytopia import Logger, Operation

# Current Project Imports

# Configuration
logger = Logger(log_level="INFO")


# Classes
class CommentCode(Operation):
    def __init__(self, file_path: Path, code_content: str = ""):
        self.file_path = file_path
        self.code_content = code_content
        self.language = "swift" if self.file_path.suffix.lstrip(".") == "swift" else "python"

    async def execute(self):
        file_content = self.code_content or self.file_path.read_text()
        text = f"Documentation for {self.file_path.name}"
        box_width = 115
        text_length = len(text)
        padding = (box_width - 2 - text_length) // 2
        is_swift = self.language == "swift"
        opening, closing = ("/**", "**/") if is_swift else ('"""', '"""')
        box_border = "═" * (box_width - 2)
        box_content = " " * padding + text + " " * (box_width - 2 - padding - text_length)
        new_docstring = f"{opening}\n╔{box_border}╗\n║{box_content}║\n╚{box_border}╝\n{closing}"
        docstring_pattern = r"^/\*\*\s*[\s\S]*?\*/" if is_swift else r'^("""|\'\'\')\s*[\s\S]*?\1'

        stripped_content = file_content.strip()
        if re.match(docstring_pattern, stripped_content):
            new_content = re.sub(docstring_pattern, new_docstring, stripped_content, count=1)
        else:
            new_content = f"{new_docstring}\n\n{file_content}"

        return new_content
