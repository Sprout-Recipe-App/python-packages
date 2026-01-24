from watchfiles import Change

from dev_pytopia.terminal_functionality.commands.execute_and_restart_program.program_restarter.program_restarter import (
    ProgramRestarter,
)

from ...operations.add_template_to_project import AddTemplateToProject
from ...operations.save_directory_structure import SaveDirectoryStructure


class FileSystemChangeResponder:
    operations_to_execute = {
        Change.added: (AddTemplateToProject, SaveDirectoryStructure),
        Change.deleted: (SaveDirectoryStructure,),
    }

    def __init__(self, configuration, file_system_state):
        self.configuration = configuration
        self._file_system_state = file_system_state

    def handle_changes(self, changes):
        return self._process_change_batch(changes)

    async def _process_change_batch(self, changes):
        async with ProgramRestarter.lock_until_complete():
            state = self._file_system_state
            for change, path in changes:
                if state.has_cooldown_active(path):
                    continue
                state.record_event(path)
                if path.is_file() and state.should_save_next_modified_file:
                    state.save_file(path)
                    continue
                for operation_class in self.operations_to_execute.get(change, ()):
                    await operation_class(path)
