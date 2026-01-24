import asyncio
import sys


class TerminalChangeProcessor:
    def __init__(self, restart_program_callback, restart_program_trigger_key="r"):
        self._restart_program_callback = restart_program_callback
        self._restart_program_trigger_key = restart_program_trigger_key

    async def process_changes(self):
        while input_text := await asyncio.to_thread(sys.stdin.readline):
            if input_text.strip() == self._restart_program_trigger_key:
                asyncio.create_task(self._restart_program_callback())
