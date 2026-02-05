import asyncio

import click

from .program_restarter.program_restarter import ProgramRestarter
from .program_restarter.supports.program_restarter_configuration import ProgramRestarterConfiguration

COMMAND_SETTINGS = {"context_settings": {"ignore_unknown_options": True, "allow_interspersed_args": False}}


@click.argument("command_and_arguments", nargs=-1)
def main(command_and_arguments):
    asyncio.run(ProgramRestarter.use(ProgramRestarterConfiguration.from_cli(command_and_arguments)))
