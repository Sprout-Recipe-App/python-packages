"""
╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                         Documentation for group_code.py                                         ║
╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# Standard Library Imports
from pathlib import Path

# Third-Party Imports
from artificial_mycelium import AI, ProgrammingFileResponse, Thread
from dev_pytopia import Logger, Operation

# Current Project Imports
from .instruction_manager import InstructionManager
from ..clean_code import CleanCode

# First-Party Imports
from ....template_provider.template_provider import TemplateProvider

# Constants
GROUP_CODE_MESSAGE_TEMPLATE = """=== TASK ===
Your task is to ensure that the file has the correct group headers!

=== FILE CONTENT TO ADD GROUP HEADERS TO ===
<<<<< The file content to add group headers to starts on the next line! >>>>>
{code_to_group}
<<<<< The previous line was the end of the file content to add group headers to! >>>>>

=== EXAMPLE TEMPLATE ===
<<<<< An example template starts on the next line >>>>>
{template_to_group_with}
<<<<< The previous line was the end of the example template >>>>>

=== INSTRUCTIONS TO FOLLOW WHILE ADDING GROUP HEADERS ===
{instructions}
"""

# Configuration
logger = Logger(log_level="INFO")


# Classes
class GroupCode(Operation):
    def __init__(self, file_path: Path, code_content: str = ""):
        self.file_path = file_path
        self.code_content = code_content
        self.file_suffix = self.file_path.suffix.lstrip(".")
        self.language = "swift" if self.file_suffix == "swift" else "python"
        self.template_file = TemplateProvider.get_template_path(self.file_path)
        self.llm_client = AI(name="5.1")
        self.instructions = InstructionManager(
            Path(__file__).parent / "instructions_for_grouping_code.yaml"
        ).get_instructions(self.file_suffix, self.template_file.name)

    async def execute(self) -> str:
        logger.info(
            f"=== Executing GroupCode ===\n  --> Grouping Code in File: {self.file_path}\n  --> Using Template: {self.template_file.name}"
        )
        code_to_group = self.code_content if self.code_content else self.file_path.read_text()
        logger.info(f"Code to Group: {code_to_group}")
        message = GROUP_CODE_MESSAGE_TEMPLATE.format(
            code_to_group=code_to_group,
            template_to_group_with=self.template_file.read_text(),
            instructions=self.instructions,
        )
        response = await self.llm_client.get_response(
            thread=Thread.add_first_message(role="user", text=message), response_format=ProgrammingFileResponse
        )
        grouped_code = response.file_content
        if self.language == "swift":
            grouped_code = CleanCode.clean_escaped_quotes_in_swift_strings(grouped_code)
        logger.info(f"Grouped Code: {grouped_code}")
        return grouped_code
