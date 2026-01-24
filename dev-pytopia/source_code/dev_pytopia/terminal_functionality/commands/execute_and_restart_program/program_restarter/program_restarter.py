import asyncio
from contextlib import AsyncExitStack, asynccontextmanager, suppress
import os
import socket

from dev_pytopia.services.file_system_change_processor.file_system_change_processor import (
    FileSystemChangeProcessor,
)
from dev_pytopia.services.file_system_change_processor.supports.file_system_change_processor_configuration import (
    FileSystemChangeProcessorConfiguration as FSConf,
)

from .supports.restartable_program import RestartableProgram
from .supports.terminal_change_processor import TerminalChangeProcessor


class ProgramRestarter:
    _global_processing_lock = asyncio.Lock()

    def __init__(self, cfg):
        self._restartable_program = RestartableProgram(cfg.command, cfg)
        self._restartable_program.setup_signal_handlers(self._restartable_program.terminate_if_running)
        self._lock_count_lock = asyncio.Lock()
        self._lock_server = None
        self._external_lock_count = 0
        self._unlocked_event = asyncio.Event()
        self._unlocked_event.set()
        self._debounce_task = None
        self._processors = [
            p
            for p in (
                cfg.enable_file_observing
                and FileSystemChangeProcessor(
                    configuration=FSConf(
                        directories_to_observe=cfg.directories_to_observe,
                        include_globs=tuple(cfg.include_globs or ()),
                        exclude_globs=tuple(cfg.exclude_globs or ()),
                    ),
                    on_changes=lambda *_: self._handle_change(),
                ),
                cfg.enable_restart_from_terminal
                and TerminalChangeProcessor(restart_program_callback=self._handle_change),
            )
            if p
        ]

    async def _start_lock_server(self):
        async def handle(reader, writer):
            command = (await reader.readline()).strip().upper()
            async with self._lock_count_lock:
                valid = command == b"LOCK" or (command == b"UNLOCK" and self._external_lock_count)
                if valid:
                    self._external_lock_count += 1 if command == b"LOCK" else -1
                    (self._unlocked_event.clear if self._external_lock_count else self._unlocked_event.set)()
                writer.write(b"OK\n" if valid else b"ERR\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        self._lock_server = await asyncio.start_server(handle, "127.0.0.1", 0)
        if sockets := self._lock_server.sockets:
            os.environ["RESTARTER_LOCK_PORT"] = str(sockets[0].getsockname()[1])

    async def _stop_lock_server(self):
        if server := self._lock_server:
            server.close()
            await server.wait_closed()

    async def _run_until_exit(self):
        await self._restartable_program.execute()
        if self._processors:
            await asyncio.gather(*(processor.process_changes() for processor in self._processors))
        else:
            await asyncio.to_thread(self._restartable_program._child_process.wait)

    async def _handle_change(self):
        if self._debounce_task:
            self._debounce_task.cancel()
        self._debounce_task = asyncio.create_task(self._debounced_restart())

    async def _debounced_restart(self):
        with suppress(Exception):
            await asyncio.sleep(0.5)
        await self._unlocked_event.wait()
        async with self._global_processing_lock:
            self._restartable_program.terminate_if_running()
            await self._restartable_program.execute()

    @classmethod
    @asynccontextmanager
    async def restarter_lock(cls):
        def send(command):
            with (
                suppress(Exception),
                socket.create_connection(
                    ("127.0.0.1", int(os.getenv("RESTARTER_LOCK_PORT", 0))), timeout=0.3
                ) as conn,
            ):
                conn.sendall(command)
                conn.recv(16)

        send(b"LOCK\n")
        try:
            yield
        finally:
            send(b"UNLOCK\n")

    @classmethod
    async def use(cls, cfg):
        restarter = cls(cfg)
        try:
            await restarter._start_lock_server()
            await restarter._run_until_exit()
        finally:
            restarter._restartable_program.terminate_if_running()
            await restarter._stop_lock_server()

    @classmethod
    @asynccontextmanager
    async def lock_until_complete(cls, *async_contexts):
        async with AsyncExitStack() as stack:
            for context in (c for c in (cls.restarter_lock(), cls._global_processing_lock, *async_contexts) if c):
                await stack.enter_async_context(context)
            yield
