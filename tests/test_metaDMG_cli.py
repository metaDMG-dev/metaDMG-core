#%%
from pathlib import Path

import pytest
from typer.testing import CliRunner

from metaDMG import __version__, utils
from metaDMG.cli.cli import cli_app


#%%


def clean() -> None:
    """Make test directory clean for new test run"""

    print("Cleaning")

    utils.remove_directory(Path("data"), missing_ok=True)
    utils.remove_directory(Path("logs"), missing_ok=True)

    for file in Path(".").glob("config*.yaml"):
        utils.remove_file(file)

    for file in Path(".").glob("*.csv"):
        utils.remove_file(file)

    for file in Path(".").glob("*.tsv"):
        utils.remove_file(file)

    for file in Path(".").glob("*.gz"):
        utils.remove_file(file)

    for file in Path(".").glob("*.pdf"):
        utils.remove_file(file)

    for file in Path(".").glob("*.pdf"):
        utils.remove_file(file)


# clean()


#%%

runner = CliRunner()


def test_version():
    assert __version__ >= "0.1.0"


def test_CLI_version():
    result = runner.invoke(cli_app, ["--version"])
    assert result.exit_code == 0
    assert "metaDMG CLI" in result.stdout


def test_CLI_config_LCA_without_names():
    result = runner.invoke(cli_app, ["config", "./testdata/alignment.bam"])
    assert result.exit_code != 0
    assert "are mandatory when doing" in result.stdout


config_lca_path = Path("config_lca.yaml")

other_path = Path("data") / "other"

csv_convert_path = other_path / "out-convert.csv"
csv_convert_with_preds_path = other_path / "out-convert-with-predictions.csv"
csv_filter_path = other_path / "out-filter.csv"
pdf_plot_path = other_path / "pdf_export.pdf"
pmd_path = Path("data") / "pmd" / "alignment.pmd.txt.gz"


LCA_commands = [
    "config",
    "testdata/alignment.bam",
    "--names",
    "testdata/names-mdmg.dmp",
    "--nodes",
    "testdata/nodes-mdmg.dmp",
    "--acc2tax",
    "testdata/acc2taxid.map.gz",
    "--metaDMG-cpp",
    "../metaDMG-cpp",
    "--custom-database",
    "--config-file",
    str(config_lca_path),
]


def test_clean():
    other_path.mkdir(parents=True, exist_ok=True)
    assert 0 == 0


def test_CLI_config_LCA1():
    result = runner.invoke(cli_app, LCA_commands)
    assert "Do you want to overwrite it" not in result.stdout
    assert f"{str(config_lca_path)} was created" in result.stdout
    assert result.exit_code == 0


def test_CLI_config_LCA2():
    """Running the same code twice should not produce a new config file"""
    result = runner.invoke(cli_app, LCA_commands)
    assert "Do you want to overwrite it" in result.stdout
    assert "Exiting" in result.stdout
    assert "Aborted" in result.stdout
    assert result.exit_code != 0


def test_CLI_config_LCA3():
    """Running the same code twice should not produce a new config file, except when entering 'y'"""
    result = runner.invoke(cli_app, LCA_commands, input="\n")  # just enter
    assert "Do you want to overwrite it" in result.stdout
    assert "Exiting" in result.stdout
    assert "Aborted" in result.stdout
    assert result.exit_code != 0


def test_CLI_config_LCA4():
    """Running the same code twice should not produce a new config file, except when entering 'y'"""
    result = runner.invoke(cli_app, LCA_commands, input="y\n")  # press y
    assert "Do you want to overwrite it" in result.stdout
    assert f"{str(config_lca_path)} was created" in result.stdout
    assert result.exit_code == 0


def test_CLI_compute_bad1():
    result = runner.invoke(cli_app, ["compute"])
    assert result.exit_code != 0


def test_CLI_compute_bad2():
    result = runner.invoke(cli_app, ["compute", "blabla"])
    assert result.exit_code != 0


def test_CLI_compute():
    result = runner.invoke(cli_app, ["compute", str(config_lca_path)])
    assert result.exit_code == 0


# # CANNOT TEST WORKING DASHBOARD CLI
# def test_CLI_dashboard():
#     result = runner.invoke(cli_app, ["dashboard", str(config_lca_path)])
#     assert result.exit_code == 0


def test_CLI_convert_bad1():
    result = runner.invoke(cli_app, ["convert"])
    assert "Missing option '--output'" in result.stdout
    assert result.exit_code != 0


def test_CLI_convert_bad2():
    result = runner.invoke(cli_app, ["convert", str(config_lca_path)])
    assert "Missing option '--output'" in result.stdout
    assert result.exit_code != 0


def test_CLI_convert_bad3():
    result = runner.invoke(cli_app, ["convert", "--output", str(csv_convert_path)])
    assert "Aborted" in result.stdout
    assert result.exit_code != 0


def test_CLI_convert1():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(csv_convert_path),
        ],
    )
    # no errors
    assert result.exit_code == 0

    # outfile exists
    assert csv_convert_path.is_file()

    # outfile is not empty
    assert csv_convert_path.stat().st_size > 0


def test_CLI_convert2():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(csv_convert_with_preds_path),
            "--add-fit-predictions",
        ],
    )
    # no errors
    assert result.exit_code == 0

    # outfile exists
    assert csv_convert_with_preds_path.is_file()

    # outfile is not empty
    assert csv_convert_with_preds_path.stat().st_size > 0

    import pandas as pd

    df = pd.read_csv(csv_convert_with_preds_path)
    assert df.shape == (14, 223)

    assert "Dx+1" in df.columns
    assert "Dx-1" in df.columns

    assert "Dx_std+1" in df.columns
    assert "Dx_std-1" in df.columns


def test_CLI_convert3():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(other_path / "testconvert.csv"),
        ],
    )
    # no errors
    assert result.exit_code == 0


def test_CLI_convert4():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(other_path / "testconvert.tsv"),
        ],
    )
    # no errors
    assert result.exit_code == 0


def test_CLI_convert5():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(other_path / "testconvert.csv.gz"),
        ],
    )
    # no errors
    assert result.exit_code == 0


def test_CLI_convert6():
    result = runner.invoke(
        cli_app,
        [
            "convert",
            str(config_lca_path),
            "--output",
            str(other_path / "testconvert.tsv.gz"),
        ],
    )
    # no errors
    assert result.exit_code == 0


def test_CLI_filter():
    result = runner.invoke(
        cli_app,
        [
            "filter",
            str(config_lca_path),
            "--output",
            str(csv_filter_path),
            "--query",
            "N_reads > 10_000",
        ],
    )
    # no errors
    assert result.exit_code == 0

    # outfile exists
    assert csv_filter_path.is_file()

    # outfile is not empty
    assert csv_filter_path.stat().st_size > 0

    import pandas as pd

    df = pd.read_csv(csv_filter_path)
    assert df.shape == (8, 163)


def test_CLI_plot():
    result = runner.invoke(
        cli_app,
        [
            "plot",
            str(config_lca_path),
            "--query",
            "N_reads > 10_000",
            "--tax-ids",
            "751,6023,35550",
            "--query",
            "N_reads < 100_000",
            "--output",
            str(pdf_plot_path),
        ],
    )

    # no errors
    assert result.exit_code == 0

    # outfile exists
    assert pdf_plot_path.is_file()

    # outfile is not empty
    assert pdf_plot_path.stat().st_size > 0


def test_CLI_pmd():
    result = runner.invoke(
        cli_app,
        [
            "PMD",
            str(config_lca_path),
        ],
    )

    # no errors
    assert result.exit_code == 0

    # outfile exists
    assert pmd_path.is_file()

    # outfile is not empty
    assert pmd_path.stat().st_size > 0
