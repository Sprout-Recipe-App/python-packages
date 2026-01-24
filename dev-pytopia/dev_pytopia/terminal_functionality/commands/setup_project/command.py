import asyncio

import click

from .operations.setup_python_package import SetupPythonPackage
from ....terminal_functionality import terminal_command_registry


@terminal_command_registry.register_command(name="setup-project")
@click.argument("package_name")
def setup_python_project(package_name):
    asyncio.run(SetupPythonPackage(package_name).execute())
