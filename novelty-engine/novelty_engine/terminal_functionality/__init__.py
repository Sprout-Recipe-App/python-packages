from dev_pytopia.frameworks.terminal_functionality_framework.terminal_command_registry import (
    TerminalCommandRegistry,
)

terminal_command_registry = TerminalCommandRegistry()


def main() -> None:
    terminal_command_registry.run()
