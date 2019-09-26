"""myapps cli tests."""

from click.testing import CliRunner
import pytest

from myapps import cli


def test_patch_settings_command():
    """Sample test for say_message command."""
    runner = CliRunner()
    params = ["patch-settings"]
    result = runner.invoke(cli.main, params)
    assert "Patching settings: Hello World 1.0.0 GRCh37" in result.output
