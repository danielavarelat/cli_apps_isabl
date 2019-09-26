"""
myapps commands.

Commands added to `main` will be available with `myapps --help`.
You can also have new commands available under `isabl --help`, see CUSTOM_COMMANDS in
https://docs.isabl.io/isabl-settings.
"""
import click

from isabl_cli import __version__ as isabl_version

from myapps import __version__
from myapps import apps


@click.group()
@click.version_option(version=f'{__version__} (isabl-cli {isabl_version})')
def main():  # pragma: no cover
    """myapps commands."""
    pass


@click.command()
def patch_settings():
    """Patch settings here if you want to version controll them."""
    apps.HelloWorldApp().patch_application_settings(echo_path="echo")


main.add_command(patch_settings)
