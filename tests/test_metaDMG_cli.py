#%%
from pathlib import Path

import pytest
from typer.testing import CliRunner

from metaDMG import __version__, utils
from metaDMG.cli.cli import cli_app


#%%

runner = CliRunner()


def clean_test_dir() -> None:
    """Make test directory clean for new test run"""

    print("Cleaning")

    utils.remove_directory("data/", missing_ok=True)
    utils.remove_directory("logs/", missing_ok=True)

    for file in Path(".").glob("*.yaml"):
        utils.remove_file(file)

    for file in Path(".").glob("*.csv"):
        utils.remove_file(file)

    for file in Path(".").glob("*.pdf"):
        utils.remove_file(file)


clean_test_dir()


#%%


def test_version():
    assert __version__ >= "0.1.0"


def test_CLI_version():
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert "metaDMG CLI" in result.stdout


def test_CLI_config_LCA_without_names():
    result = runner.invoke(cli_app, ["config", "./test/alignment.bam"])
    assert result.exit_code != 0
    assert "are mandatory when doing" in result.stdout


LCA_commands = [
    "config",
    "./testdata/alignment.bam",
    "--names",
    "testdata/names-mdmg.dmp",
    "--nodes",
    "testdata/nodes-mdmg.dmp",
    "--acc2tax",
    "testdata/acc2taxid.map.gz",
    "--metadmg-cpp",
    "../metaDMG-cpp",
    "--fix-ncbi",  # is not a NCBI database, so do not fix
    "0",
    "--config-path",
    "config_lca.yaml",
]


def test_CLI_config_LCA1():
    result = runner.invoke(cli_app, LCA_commands)
    assert "Do you want to overwrite it" not in result.stdout
    assert "Config file was created" in result.stdout
    assert result.exit_code == 0


def test_CLI_config_LCA2():
    """Running the same code twice should not produce a new config file"""
    result = runner.invoke(cli_app, LCA_commands)
    assert "Do you want to overwrite it" in result.stdout
    assert "Exiting" in result.stdout
    assert "Aborted" in result.stdout
    assert "Config file was created" not in result.stdout
    assert result.exit_code != 0


def test_CLI_config_LCA3():
    """Running the same code twice should not produce a new config file, except when entering 'y'"""
    result = runner.invoke(cli_app, LCA_commands, input="\n")  # just enter
    assert "Do you want to overwrite it" in result.stdout
    assert "Exiting" in result.stdout
    assert "Aborted" in result.stdout
    assert "Config file was created" not in result.stdout
    assert result.exit_code != 0


def test_CLI_config_LCA4():
    """Running the same code twice should not produce a new config file, except when entering 'y'"""
    result = runner.invoke(cli_app, LCA_commands, input="y\n")  # press y
    assert "Do you want to overwrite it" in result.stdout
    assert "Config file was created" in result.stdout
    assert result.exit_code == 0


def test_CLI_compute_bad1():
    result = runner.invoke(cli_app, ["compute"])
    assert result.exit_code != 0


def test_CLI_compute_bad2():
    result = runner.invoke(cli_app, ["compute", "blabla"])
    assert result.exit_code != 0


def test_CLI_compute():
    result = runner.invoke(cli_app, ["compute", "config_lca.yaml"])
    assert result.exit_code == 0


def test_CLI_dashboard_bad():
    result = runner.invoke(cli_app, ["dashboard"])
    assert result.exit_code != 0


# # CANNOT TEST WORKING DASHBOARD CLI
# def test_CLI_dashboard():
#     result = runner.invoke(cli_app, ["dashboard", "config_lca.yaml"])
#     assert result.exit_code == 0


def test_CLI_convert_bad1():
    result = runner.invoke(cli_app, ["convert"])
    assert "Missing option '--output'" in result.stdout
    assert result.exit_code != 0


def test_CLI_convert_bad2():
    result = runner.invoke(cli_app, ["convert", "config_lca.yaml"])
    assert "Missing option '--output'" in result.stdout
    assert result.exit_code != 0


def test_CLI_convert_bad3():
    result = runner.invoke(cli_app, ["convert", "--output", "out-convert.csv"])
    assert result.exit_code != 0


def test_CLI_convert1():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            "config_lca.yaml",
            "--output",
            "out-convert.csv",
        ],
    )
    # no errors
    assert result.exit_code == 0

    outfile = Path("out-convert.csv")

    # outfile exists
    assert outfile.is_file()

    # outfile is not empty
    assert outfile.stat().st_size > 0


def test_CLI_convert2():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            "config_lca.yaml",
            "--output",
            "out-convert-with-fit-predictions.csv",
            "--add-fit-predictions",
        ],
    )
    # no errors
    assert result.exit_code == 0

    outfile = Path("out-convert-with-fit-predictions.csv")

    # outfile exists
    assert outfile.is_file()

    # outfile is not empty
    assert outfile.stat().st_size > 0

    import pandas as pd

    df = pd.read_csv(outfile)
    assert df.shape == (14, 223)

    assert "Dx+1" in df.columns
    assert "Dx-1" in df.columns

    assert "Dx_std+1" in df.columns
    assert "Dx_std-1" in df.columns


def test_CLI_filter():
    result = runner.invoke(
        cli_app,
        [
            "filter",
            "config_lca.yaml",
            "--output",
            "out-filter.csv",
            "--query",
            "N_reads > 10_000",
        ],
    )
    # no errors
    assert result.exit_code == 0

    outfile = Path("out-filter.csv")

    # outfile exists
    assert outfile.is_file()

    # outfile is not empty
    assert outfile.stat().st_size > 0

    import pandas as pd

    df = pd.read_csv(outfile)
    assert df.shape == (8, 163)


def test_CLI_plot():
    result = runner.invoke(
        cli_app,
        [
            "plot",
            "config_lca.yaml",
            "--query",
            "N_reads > 10_000",
            "--tax-ids",
            "751,6023,35550",
            "--query",
            "N_reads < 100_000",
            "--pdf-out",
            "pdf_export.pdf",
        ],
    )

    # no errors
    assert result.exit_code == 0

    outfile = Path("pdf_export.pdf")

    # outfile exists
    assert outfile.is_file()

    # outfile is not empty
    assert outfile.stat().st_size > 0
