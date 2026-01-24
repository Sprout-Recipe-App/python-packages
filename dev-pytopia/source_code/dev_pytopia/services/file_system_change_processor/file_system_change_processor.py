import asyncio
from pathlib import Path
from typing import Awaitable, Callable

from watchfiles import awatch

from .supports.file_system_change_processor_configuration import FileSystemChangeProcessorConfiguration


class FileSystemChangeProcessor:
    def __init__(
        self,
        configuration: FileSystemChangeProcessorConfiguration,
        on_changes: Callable[[set], Awaitable[None] | None] | None = None,
    ) -> None:
        self.configuration = configuration
        self._on_changes = on_changes

    def _should_watch(self, _, path: str) -> bool:
        if Path(path).is_dir():
            return True
        included = not self.configuration._include_spec or self.configuration._include_spec.match_file(path)
        excluded = self.configuration._exclude_spec and self.configuration._exclude_spec.match_file(path)
        return included and not excluded

    async def process_changes(self) -> None:
        async for changes in awatch(
            *self.configuration.directories_to_observe,
            watch_filter=self._should_watch,
            debounce=self.configuration.processing_debounce,
        ):
            if changes:
                self.handle_changes({(change, Path(path)) for change, path in changes})

    def handle_changes(self, changes: set) -> None:
        if not self._on_changes:
            raise NotImplementedError
        if asyncio.iscoroutine(result := self._on_changes(changes)):
            asyncio.create_task(result)
