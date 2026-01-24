"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ Documentation for organize_code.py
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# Standard library imports
from pathlib import Path
from typing import cast

from artificial_mycelium import AI, LLMCodeResponse, Thread
from coding_guru.v1.terminal_functionality.commands.observe_and_improve_codebase.template_provider.template_provider import (
    TemplateProvider,
)

# Current project imports
# Local development package imports
from dev_pytopia import Logger, Operation
from dev_pytopia.terminal_functionality.commands.execute_and_restart_program.program_restarter.program_restarter import (
    ProgramRestarter,
)

from .instruction_manager import (
    InstructionManager,
)
from ..clean_code import CleanCode

# Current project imports

# Configuration
logger = Logger(log_level="INFO")

# Constants
COMMENT_STYLES = {
    "swift": {"line_comment": "//", "doc_comment": "///"},
    "python": {"line_comment": "#", "block_start": '"""', "block_end": '"""'},
}
DEFAULT_COMMENT_STYLE = COMMENT_STYLES["python"]
ORGANIZED_CODE_MARKER = "{comment_style} THIS CODE HAS BEEN ORGANIZED"
ORIGINAL_CODE_COMMENT_START = "\n\n/* Original code before organization:"
ORIGINAL_CODE_COMMENT_END = "\n*/\n"
ORGANIZING_MARKER = "{comment_style} LLM IS CURRENTLY ORGANIZING CODE...\n"

ORGANIZE_CODE_MESSAGE_TEMPLATE = """\
=== TASK ===
Your task is to organize the provided code by conforming to the template structure.

=== KNOWN MISTAKES TO FIX ===
{mistakes_to_fix}

=== CODE TO ORGANIZE ===
<<<<< The code to organize starts on the next line >>>>>
{code_to_organize}
<<<<< The previous line was the end of the code to organize >>>>>

=== TEMPLATE TO ORGANIZE CODE WITH ===
<<<<< The template to organize the code with starts on the next line >>>>>
{template_to_organize_with}
<<<<< The previous line was the end of the template to organize the code with >>>>>

=== INSTRUCTIONS TO FOLLOW WHILE ORGANIZING CODE ===
{instructions}

=== Extra Information ===
Name of file being organized: {file_name}
Directory file being organized in: {directory_path}"""

IDENTIFY_MISTAKES_MESSAGE_TEMPLATE = """\
=== TASK ===
Your task is to review the provided code that was organized by a LLM and identify any mistakes it made.
Verify that all of the instructions specified below were followed correctly.

=== INSTRUCTIONS THAT WERE GIVEN TO THE LLM ===
{instructions}

=== ORGANIZED CODE TO CHECK FOR MISTAKES ===
<<<<< The organized code to check starts on the next line >>>>>
{code_to_organize}
<<<<< The previous line was the end of the organized code >>>>>

=== TEMPLATE FOR REFERENCE ===
<<<<< The template for reference starts on the next line >>>>>
{template_to_organize_with}
<<<<< The previous line was the end of the template >>>>>

=== RESPONSE FORMAT ===
You MUST respond in ONE of these two ways:

Way 1 - If mistakes are found:
    MISTAKE #1:
        Description: <clear explanation of the mistake>
        Location:    <specific context where mistake occurs>
        Correction:  <exact code that should be used instead>
    
    MISTAKE #2:
        Description: <clear explanation of the mistake>
        Location:    <specific context where mistake occurs>
        Correction:  <exact code that should be used instead>
    ... and so on for each mistake ...

Way 2 - If no mistakes are found:
    Your response should be 'No mistakes found!' and nothing else.

No other responses are allowed!"""


# Classes
class OrganizeCode(Operation):
    # __init__ and other dunder methods
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.llm_client = AI(name="5.1")
        self.file_suffix = self.file_path.suffix.lstrip(".")
        self.language = "swift" if self.file_suffix == "swift" else "python"
        self.comment_style = COMMENT_STYLES.get(self.language, DEFAULT_COMMENT_STYLE)

        self._initialize_template()
        self._initialize_instructions()

    # Public methods
    async def execute(self) -> None:
        logger.info(
            f"=== Executing OrganizeCode Operation ===\n"
            f"-> Organizing File: {self.file_path.name}\n"
            f"-> Using Template: {self.template_file.name}"
        )

        async with ProgramRestarter.restarter_lock():
            # Step 1: Get clean code for organization (removes any existing markers)
            original_code = cast(
                str, await CleanCode(self.file_path, save_to_file=False, remove_organization_marker=True)
            )

            # Step 2: Show organization in progress
            self._write_temp_file_with_marker(cast(str, original_code))

            # Step 3: Organize and validate the code
            organized_code = await self._organize_with_mistake_checking(cast(str, original_code))

            # Step 4: Write final organized code with marker and original code
            self._write_organized_code_to_file(organized_code, cast(str, original_code))
            logger.info(f"=== Completed Organize Code Operation for {self.file_path} ===")

    # Protected methods
    def _initialize_template(self) -> None:
        self.template_file = TemplateProvider.get_template_path(self.file_path)
        self.template = self.template_file.read_text()

    def _initialize_instructions(self) -> None:
        instructions_path = Path(__file__).resolve().parent / "instructions_for_organizing_code.yaml"
        self.instruction_manager = InstructionManager(instructions_path)
        self.instructions = self.instruction_manager.get_instructions(self.file_suffix, self.template_file.name)

    def _write_temp_file_with_marker(self, code: str) -> None:
        self.file_path.write_text(
            f"{ORGANIZING_MARKER.format(comment_style=self.comment_style['line_comment'])}\n{code}"
        )

    def _write_organized_code_to_file(self, organized_code: str, original_code: str) -> None:
        """Write the final organized code with the organization marker and original code in comments."""
        comment_style = self.comment_style["line_comment"]
        content = (
            f"{ORGANIZED_CODE_MARKER.format(comment_style=comment_style)}\n\n"
            f"{organized_code}\n\n"
            f"{comment_style} Original code before organization:\n"
            f"{self._comment_code(original_code)}\n"
        )
        self.file_path.write_text(content)

    def _comment_code(self, code: str) -> str:
        """Convert code into commented lines."""
        return "\n".join(f"{self.comment_style['line_comment']} {line}" for line in code.splitlines())

    async def _organize_with_mistake_checking(self, initial_code: str) -> str:
        organized_code = await self._perform_organization(
            initial_code,
            self.template,
            "No mistakes have been made yet as you haven't tried organizing the code yet.",
        )

        for round_num in range(1, 5):
            mistakes = await self._identify_mistakes(organized_code, self.template, round_num)
            if mistakes.lower() == "no mistakes found!":
                logger.info(f"No mistakes found in round {round_num}")
                break
            organized_code = await self._perform_organization(organized_code, self.template, mistakes)
        return organized_code

    async def _identify_mistakes(
        self, code_to_organize: str, template_to_organize_with: str, round_num: int
    ) -> str:
        # Configure model for mistake identification; using 5-mini for speed.
        self.llm_client = AI(name="5-mini")
        identify_mistakes_message = IDENTIFY_MISTAKES_MESSAGE_TEMPLATE.format(
            code_to_organize=code_to_organize,
            template_to_organize_with=template_to_organize_with,
            instructions=self.instructions,
        )
        llm_thread = Thread.add_first_message(role="user", text=identify_mistakes_message)
        logger.info(
            f"=== About to Send Messages to LLM to Identify Mistakes (Round {round_num}) ===\n\n"
            f"-> Intended Output: List of mistakes or 'No mistakes found!'\n\n"
            f"{llm_thread.get_printable_representation()}"
        )
        identify_mistakes_response = await self.llm_client.get_response(thread=llm_thread)
        return identify_mistakes_response.choices[0].message.content.strip()

    async def _perform_organization(
        self,
        code_to_organize: str,
        template_to_organize_with: str,
        mistakes_to_fix: str,
    ) -> str:
        # Configure model for organization output; using 5.1 for quality.
        self.llm_client = AI(name="5.1")

        message = ORGANIZE_CODE_MESSAGE_TEMPLATE.format(
            code_to_organize=code_to_organize,
            template_to_organize_with=template_to_organize_with,
            mistakes_to_fix=mistakes_to_fix,
            instructions=self.instructions,
            file_name=self.file_path.name,
            directory_path=self.file_path.parent.name,
        )
        llm_thread = Thread.add_first_message(role="user", text=message)
        logger.info(
            f"=== About to Send Messages to LLM to Organize Code ===\n\n-> Intended Output: Organized code\n\n"
            f"{llm_thread.get_printable_representation()}"
        )
        response = await self.llm_client.get_response(thread=llm_thread, response_format=LLMCodeResponse)
        organized_code = response.code

        if self.language == "swift":
            organized_code = CleanCode.clean_escaped_quotes_in_swift_strings(organized_code)

        return organized_code
