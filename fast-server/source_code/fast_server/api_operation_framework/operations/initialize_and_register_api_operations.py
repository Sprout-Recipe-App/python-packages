import importlib.util
import inspect
from pathlib import Path
import sys

from fastapi import Depends

from dev_pytopia import Logger, Operation

from .api_operation import APIOperation
from ..dependencies.log_request_data import log_request_data


class InitializeAndRegisterAPIOperations(Operation):
    def __init__(self, app, operations_folder: Path, extra_operations: list[type] | None = None):
        self.app, self.operations_folder, self._count = app, operations_folder, 0
        self.extra_operations = extra_operations or []

    async def execute(self):
        self._register_from_folder(self.operations_folder)
        for op in self.extra_operations:
            self._register(op)
        Logger().info(f"Registered {self._count} API operations!")

    def _register_from_folder(self, folder: Path):
        root = folder.parents[3]
        sys.path.insert(0, str(root))
        try:
            for file in folder.rglob("*.py"):
                if file.name.startswith("__"):
                    continue
                name = f"{'.'.join(folder.relative_to(root).parts)}.{'.'.join(file.relative_to(folder).with_suffix('').parts)}"
                if not (spec := importlib.util.spec_from_file_location(name, file)) or not spec.loader:
                    continue
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                for _, member in inspect.getmembers(module, inspect.isclass):
                    if issubclass(member, APIOperation) and member is not APIOperation:
                        self._register(member)
        finally:
            sys.path.pop(0)

    def _register(self, operation_class: type[APIOperation]):
        operation = operation_class()
        if handler := getattr(self.app, operation.METHOD.lower(), None):
            dependencies = [Depends(log_request_data)] if operation_class.LOG_REQUESTS else []
            handler(operation.ENDPOINT_PATH, name=operation_class.__name__, dependencies=dependencies)(
                operation.execute
            )
            self._count += 1
