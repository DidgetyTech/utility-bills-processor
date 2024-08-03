"""The versions are consistent because versions are hard-coded in a few different places."""

import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner

from utility_bills_processor import __version__ as lib_version
from utility_bills_processor import cli


@pytest.fixture
def runner() -> CliRunner:
    """Instantiate the click.CliRunner as a pytest.fixture."""
    return CliRunner()


@pytest.fixture(scope="session")
def toml_version() -> str:
    """Extract the library version from pyproject.toml as a pytest.fixture.

    Returns:
        the version string
    """
    with (Path(__file__).parents[1] / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)

        return str(data["tool"]["poetry"]["version"])


def test_lib_versions_match(runner: CliRunner, toml_version: str) -> None:
    """utility_bills_processor.__version__ equals the pyproject.toml version."""
    assert lib_version == toml_version


def test_cli_versions_match(runner: CliRunner, toml_version: str) -> None:
    """<cli> --version matches the pyproject.toml version."""
    result = runner.invoke(cli.process_utility_bill, ["--version"])
    assert result.output == f"process-utility-bill, version {toml_version}\n"
