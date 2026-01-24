import asyncio
from threading import Thread

from pynput import keyboard

from dev_pytopia import FileSystemChangeProcessor
from dev_pytopia.services.file_system_change_processor.supports.file_system_change_processor_configuration import (
    FileSystemChangeProcessorConfiguration,
)

from .supports.file_system_change_handler import FileSystemChangeResponder
from .supports.file_system_state import FileSystemState
from .supports.keyboard_change_responder import KeyboardChangeResponder


class ComputerObserver:
    def __init__(self):
        loop = asyncio.new_event_loop()

        def run_event_loop():
            asyncio.set_event_loop(loop)
            try:
                loop.run_forever()
            finally:
                loop.close()

        Thread(target=run_event_loop, daemon=True).start()
        responder = FileSystemChangeResponder(
            configuration=FileSystemChangeProcessorConfiguration(
                directories_to_observe=["/Users/raw-e/Desktop/"],
                include_globs=("**/*.py", "**/*.swift"),
                exclude_globs=(),
            ),
            file_system_state=(file_system_state := FileSystemState()),
        )
        self._file_system_change_processor = FileSystemChangeProcessor(
            configuration=responder.configuration, on_changes=responder.handle_changes
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=(
                responder := KeyboardChangeResponder(file_system_state=file_system_state, event_loop=loop)
            ).handle_key_press,
            on_release=responder.handle_key_release,
        )
        self._keyboard_listener.start()

    async def start(self):
        try:
            await self._file_system_change_processor.process_changes()
        finally:
            self._keyboard_listener.stop()

    @classmethod
    def run(cls):
        asyncio.run(cls().start())
