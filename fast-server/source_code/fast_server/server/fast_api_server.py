import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Awaitable, Callable

from fastapi import FastAPI
import uvicorn

from dev_pytopia import with_error_handling
from fast_server.api_operation_framework.operations.initialize_and_register_api_operations import (
    InitializeAndRegisterAPIOperations,
)


@with_error_handling
class FastAPIServer:
    def __init__(
        self,
        port: int | None = None,
        host: str = "0.0.0.0",
        api_operations_path: Path | None = None,
        extra_operations: list[type] | None = None,
    ):
        self.port = port or int(os.getenv("PORT", os.getenv("FASTAPI_SERVER_PORT")))
        self.host, self._startup_hooks = host, []
        self.api_operations_path = (
            api_operations_path or Path(sys.modules["__main__"].__file__).parent / "api/rest_api"
        )
        self.extra_operations = extra_operations or []

    async def _lifespan(self, server):
        await InitializeAndRegisterAPIOperations(server, self.api_operations_path, self.extra_operations)
        for hook in self._startup_hooks:
            await hook()
        yield

    def run(self, kill_existing: bool = True):
        if (
            kill_existing
            and not os.getenv("K_SERVICE")
            and (pids := subprocess.getoutput(f"lsof -nP -iTCP:{self.port} -sTCP:LISTEN -t").strip())
        ):
            subprocess.run(["kill", "-9", *pids.split()], stderr=subprocess.DEVNULL), time.sleep(0.3)
        uvicorn.run(FastAPI(lifespan=self._lifespan), host=self.host, port=self.port, access_log=False)

    def add_startup_hook(self, hook: Callable[[], Awaitable[None]]):
        self._startup_hooks.append(hook)
