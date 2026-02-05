import asyncio

import click

from .operations.setup_python_package import SetupPythonPackage


@click.argument("package_name")
def main(package_name):
    asyncio.run(SetupPythonPackage(package_name).execute())
