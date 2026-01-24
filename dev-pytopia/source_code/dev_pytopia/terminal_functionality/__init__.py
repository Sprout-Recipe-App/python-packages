from ..frameworks.terminal_functionality_framework.terminal_command_registry import TerminalCommandRegistry

terminal_command_registry = TerminalCommandRegistry()

__all__ = ["terminal_command_registry"]


def main() -> None:
    terminal_command_registry.run()
