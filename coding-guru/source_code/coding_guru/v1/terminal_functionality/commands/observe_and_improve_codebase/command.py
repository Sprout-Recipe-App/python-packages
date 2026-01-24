from .computer_observer.computer_observer import ComputerObserver
from ....terminal_functionality import terminal_command_registry


@terminal_command_registry.register_command(name="observe-and-improve-codebase")
def observe_and_improve_codebase() -> None:
    ComputerObserver.run()
