from metaDMG import __version__
from typer.testing import CliRunner
from metaDMG.cli.cli import cli_app


def test_version():
    assert __version__ >= "0.1.0"


runner = CliRunner()


def test_cli_app_version_version():
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert "metaDMG CLI" in result.stdout


def test_cli_app_version_command():
    result = runner.invoke(cli_app, ["compute", "blabla"])
    assert result.exit_code == 1
