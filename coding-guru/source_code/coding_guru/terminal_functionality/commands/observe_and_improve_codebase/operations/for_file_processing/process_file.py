from typing import cast

from coding_guru.terminal_functionality.commands.observe_and_improve_codebase.operations.for_file_processing.comment_code import (
    CommentCode,
)
from dev_pytopia import Operation
from dev_pytopia.terminal_functionality.commands.execute_and_restart_program.program_restarter.program_restarter import (
    ProgramRestarter,
)

from .organize_code.group_code import GroupCode


def create_formatted_marker_line(marker_text: str, line_comment: str) -> str:
    remaining_space = 115 - (len(line_comment) + 1) - len(marker_text) - 2
    equal_signs_each_side, extra_equal = divmod(remaining_space, 2)
    return (
        f"{line_comment} {'=' * equal_signs_each_side} {marker_text} {'=' * (equal_signs_each_side + extra_equal)}"
    )


class ProcessFile(Operation):
    def __init__(self, file_path):
        self.file_path = file_path
        self.line_comment = "//" if self.file_path.suffix == ".swift" else "#"

    async def execute(self):
        async with ProgramRestarter.restarter_lock():
            original_code = self.file_path.read_text()
            self.file_path.write_text(
                f"{create_formatted_marker_line('THIS FILE IS BEING PROCESSED', self.line_comment)}\n\n{original_code}"
            )
            grouped_code = cast(str, await GroupCode(self.file_path, original_code))
            commented_code = cast(str, await CommentCode(self.file_path, grouped_code))
            commented_original = "\n".join(f"{self.line_comment} {line}" for line in original_code.splitlines())
            self.file_path.write_text(
                f"{create_formatted_marker_line('THIS CODE HAS BEEN PROCESSED!', self.line_comment)}\n\n"
                f"{commented_code}\n\n"
                f"{create_formatted_marker_line('ORIGINAL CODE BEFORE PROCESSING', self.line_comment)}\n"
                f"{commented_original}\n"
            )
