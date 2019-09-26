from os.path import abspath
from os.path import dirname
from os.path import join
from pathlib import Path

from isabl_cli.settings import _DEFAULTS
import pytest

ROOT = abspath(dirname(__file__))
DATA = join(ROOT, "data")


def pytest_addoption(parser):
    """Add option to commit or not applications."""
    parser.addoption("--commit", action="store_true", help="commit applications")


@pytest.fixture
def commit(request):
    """Return true if user wants to commit the test applications."""
    return request.config.getoption("--commit")


@pytest.fixture(scope="session")
def datadir():
    """Return path to test data directory."""
    return Path(DATA)


@pytest.fixture(scope="session")
def tmpdir(tmpdir_factory):
    """Set the base storage directory as the current tmpdir."""
    ret = tmpdir_factory.mktemp("data")
    _DEFAULTS["BASE_STORAGE_DIRECTORY"] = ret.strpath

    def docker(image, entrypoint=None, docker_args=""):
        """Return a path to a docker script."""
        cmd = (
            "#!/usr/bin/env bash\n"
            f"docker run -v {ret.strpath}:{ret.strpath} -v {DATA}:{DATA} {docker_args} "
        )

        if entrypoint:
            cmd = f"{cmd} --entrypoint={entrypoint}"

        script = ret.mkdtemp().join("script")
        script.write(f'{cmd} {image} "$@" ')
        script.chmod(0o777)
        return script.strpath

    ret.docker = docker
    return ret
