"""mycli cli tests."""

from click.testing import CliRunner
import pytest

from mycli import cli


def test_main():
    """Sample test for main command."""
    runner = CliRunner()
    params = ["--help"]
    result = runner.invoke(cli.main, params)
    assert "mycli" in result.output
