"""myapps cli tests."""

from click.testing import CliRunner
import pytest

from myapps import cli


def test_main():
    """Sample test for main command."""
    runner = CliRunner()
    params = ["--help"]
    result = runner.invoke(cli.main, params)
    assert "myapps" in result.output
