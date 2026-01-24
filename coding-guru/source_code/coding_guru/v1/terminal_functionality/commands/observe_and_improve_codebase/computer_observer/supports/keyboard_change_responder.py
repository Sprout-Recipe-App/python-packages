import asyncio

from ...operations.for_file_processing.clean_code import CleanCode
from ...operations.for_file_processing.process_file import ProcessFile


class KeyboardChangeResponder:
    def __init__(self, file_system_state, event_loop):
        self._keyboard_state, self._file_system_state, self._event_loop = {}, file_system_state, event_loop

    def handle_key_press(self, key):
        if not key:
            return
        state = self._keyboard_state
        state[str(key)] = True
        if not state.get("Key.cmd"):
            return
        if state.get("'s'"):
            self._file_system_state.set_save_next_modified_file()
        elif state.get("Key.alt"):
            self._run_async(self._process_file(ProcessFile))
        elif state.get("'c'"):
            self._run_async(self._process_file(CleanCode, save_to_file=True, remove_markers=True))

    def handle_key_release(self, key):
        if key:
            self._keyboard_state[str(key)] = False

    def _run_async(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self._event_loop)

    async def _process_file(self, processor_class, **kwargs):
        if file := self._file_system_state.last_saved_file:
            await processor_class(file, **kwargs)
            self._file_system_state.clear_last_saved_file()
