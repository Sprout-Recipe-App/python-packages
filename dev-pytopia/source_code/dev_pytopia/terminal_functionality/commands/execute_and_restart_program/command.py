import asyncio

import click

from dev_pytopia.terminal_functionality import terminal_command_registry

from .program_restarter.program_restarter import ProgramRestarter
from .program_restarter.supports.program_restarter_configuration import ProgramRestarterConfiguration


@terminal_command_registry.register_command("execute-and-restart-program", context_settings=dict(ignore_unknown_options=True, allow_interspersed_args=False))
@click.argument("command_and_arguments", nargs=-1)
def execute_and_restart_program_automatically(command_and_arguments):
    asyncio.run(ProgramRestarter.use(ProgramRestarterConfiguration.from_cli(command_and_arguments)))
