from enum import IntEnum
from inspect import currentframe
import logging
from os.path import relpath

from .operations.get_location_of_log_call import GetLocationOfLogCall
from .terminal_formatter import TerminalFormatter


class Logger(logging.Logger):
    class LogLevel(IntEnum):
        TRACE, INSPECT, SEARCH, OBSERVE, INFO, CONCERN, SUSPECT, ERROR, DANGER, SHOWSTOPPER = range(10, 110, 10)

    def __init__(self, log_level="INFO"):
        frame = currentframe().f_back
        super().__init__(relpath(frame.f_code.co_filename).removesuffix(".py") if frame else __name__)

        handler = logging.StreamHandler()
        handler.setFormatter(TerminalFormatter())
        self.addHandler(handler)

        for level in self.LogLevel:
            logging.addLevelName(level.value, level.name)
            if level.name.lower() in ("info", "error"):
                setattr(
                    self,
                    level.name.lower(),
                    lambda msg, *a, lv=level.value, stacklevel=1, **kw: self.log(
                        lv, msg, *a, stacklevel=stacklevel, **kw
                    ),
                )

        self.setLevel(getattr(self.LogLevel, log_level.upper(), self.LogLevel.INFO).value)

    def _log(self, level, message, args, **kwargs):
        location = GetLocationOfLogCall(currentframe().f_back, kwargs.pop("stacklevel", 1))()
        super()._log(level, f"{location}\nCONTENT:\n{message}", args, **kwargs)

    def __getattr__(self, name):
        level = getattr(self.LogLevel, name.upper(), None)
        return (
            (lambda msg, *a, stacklevel=1, **kw: self.log(level.value, msg, *a, stacklevel=stacklevel, **kw))
            if level
            else (lambda *a, **kw: None)
        )
