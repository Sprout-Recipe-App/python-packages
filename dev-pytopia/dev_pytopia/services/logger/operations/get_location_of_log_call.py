from inspect import getfile
from types import FrameType
from typing import NamedTuple

from ....frameworks.operation_framework.operation import Operation


class LogCallerInfo(NamedTuple):
    package_name: str | None
    caller_type: str
    full_path: str
    line_number: int


class GetLocationOfLogCall(Operation):
    def __init__(self, caller_frame: FrameType | None = None, stack_level: int = 1) -> None:
        super().__init__()
        self.caller_frame, self.stack_level = caller_frame, stack_level

    def execute(self) -> str:
        callers = self._gather_location_data()
        return self._generate_output_string(callers) if callers else ""

    def _get_caller_type(self, name: str, lvars: dict) -> str:
        if name == "<module>":
            return "Module"
        if name == "<lambda>":
            return "Lambda"
        if "self" in lvars:
            class_type = type(lvars["self"])
            kind = "Property" if isinstance(getattr(class_type, name, None), property) else "Method"
            return f"{kind} {name} of {class_type.__name__}"
        if "cls" in lvars:
            return f"Classmethod {name} of {lvars['cls'].__name__}"
        if "decorator" in name.lower() or name.startswith("_wrapper"):
            return f"Decorator {name}"
        return f"Function {name}"

    def _gather_location_data(self) -> list[LogCallerInfo] | None:
        def is_internal(path: str) -> bool:
            return (
                path.endswith(("/logger.py", "/terminal_formatter.py"))
                or "/services/logger/operations/" in path
                or "/logging/" in path
            )

        frame = self.caller_frame
        while frame and is_internal(getfile(frame)):
            frame = frame.f_back

        callers = []
        for _ in range(self.stack_level):
            if not frame:
                break
            path = getfile(frame)
            package_name = path.split("My Packages/", 1)[1].split("/", 1)[0] if "My Packages/" in path else None
            callers.append(
                LogCallerInfo(
                    package_name, self._get_caller_type(frame.f_code.co_name, frame.f_locals), path, frame.f_lineno
                )
            )
            frame = frame.f_back

        return callers or None

    def _generate_output_string(self, location_data: list[LogCallerInfo]) -> str:
        output = ["\n    📍 Location:"]
        for i, caller in enumerate(location_data):
            indent = "    " * i
            prefix = f"\n        {indent}↳\n            {indent}" if i else "\n        "
            line_prefix = f"\n            {indent}" if i else "\n        "

            if caller.package_name:
                output.append(f"{prefix}🔹 Package: {caller.package_name}")
            output.append(f"{line_prefix}🔹 From: {caller.caller_type} L{caller.line_number}")
            output.append(f"{line_prefix}🔹 Path: {caller.full_path}")
        return "".join(output)
