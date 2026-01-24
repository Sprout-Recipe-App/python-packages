from contextlib import suppress
import os
import signal
import subprocess
import sys


class RestartableProgram:
    def __init__(self, command, configuration):
        self._command, self.configuration, self._child_process = command, configuration, None

    async def execute(self):
        self.terminate_if_running()
        self._child_process = subprocess.Popen(
            list(self._command),
            env=os.environ
            | {
                "PYTHONUNBUFFERED": "1",
                "COMMAND_EXECUTION_PATH": os.environ.get("COMMAND_EXECUTION_PATH")
                or str(next(iter(getattr(self.configuration, "directories_to_observe", [])), os.getcwd())),
            },
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin,
            start_new_session=True,
        )

    def setup_signal_handlers(self, cleanup_callback):
        for s in signal.SIGTERM, signal.SIGINT, signal.SIGQUIT:
            signal.signal(s, lambda *_: (cleanup_callback(), sys.exit()))

    def terminate_if_running(self):
        if (p := self._child_process) and p.poll() is None:
            with suppress(Exception):
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        self._child_process = None
