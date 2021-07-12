import typer
from pathlib import Path
from typing import List, Optional

from metadamageprofiler import cli_utils

cli_app = cli_utils.get_cli_app()

storage_path_default = Path("./data/")
config_file = Path("config.yaml")

#%%


@cli_app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=cli_utils.version_callback,
    ),
):
    """
    Metadamage Profiler — Profiling (Meta)Genomic Ancient Damage.

    First run the LCA and compute the ancient damage statistics with the 'compute' command:

    \b
        $ metadamageprofiler config --help

    \b
        $ metadamageprofiler compute --help

    And subsequently visualize the results using the dashboard:

    \b
        $ metadamageprofiler dashboard --help

    """


#%%


@cli_app.command("config")
def config(
    samples: List[Path] = typer.Argument(
        ...,
        help="Single or multiple alignment-files (or a directory containing them).",
    ),
    names: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) names.dmp.gz.",
    ),
    nodes: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) nodes.dmp.gz.",
    ),
    acc2tax: Path = typer.Option(
        ...,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) acc2tax.gz.",
    ),
    ngsLCA_command: Path = typer.Option(
        "ngsLCA/metadamage",
        help="The command needed to run the ngsLCA-program.",
    ),
    simscorelow: float = typer.Option(
        0.95,
        help="Normalized edit distance (read to reference similarity) minimum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 1),
    ),
    simscorehigh: float = typer.Option(
        1.0,
        help="Normalized edit distance (read to reference similarity) maximum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 1),
    ),
    editdistmin: int = typer.Option(
        0,
        help="Minimum edit distance (read to reference similarity). Number between 0-10.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 10),
    ),
    editdistmax: int = typer.Option(
        10,
        help="Maximum edit distance (read to reference similarity). Number between 0-10.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 10),
    ),
    minmapq: int = typer.Option(
        0,
        help="Minimum mapping quality.",
    ),
    max_position: int = typer.Option(
        15,
        help="Number of positions to include (|z| < max_position).",
    ),
    lca_rank: cli_utils.RANKS = typer.Option(
        cli_utils.RANKS.none,
        case_sensitive=False,
        help="The LCA rank used in ngsLCA.",
    ),
    storage_path: Path = typer.Option(
        storage_path_default,
        help="Path where the generated output files and folders are stored.",
    ),
    cores: int = typer.Option(
        1,
        help="The maximum number of cores to use in the ancient damage estimation.",
    ),
    bayesian: bool = typer.Option(
        False,
        "--bayesian",
        help="Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Debug mode.",
    ),
):
    """Generate the config file."""

    from metadamageprofiler import utils
    import yaml

    d_paths = {
        "ngsLCA": storage_path / "ngsLCA",
        "mismatch": storage_path / "mismatch",
        "fit_results": storage_path / "fit_results",
        "results": storage_path / "results",
        "database": storage_path / "database",
    }

    config = utils.remove_paths(
        {
            "samples": utils.extract_alignments(samples),
            #
            "ngsLCA_command": ngsLCA_command,
            "names": names,
            "nodes": nodes,
            "acc2tax": acc2tax,
            "simscorelow": simscorelow,
            "simscorehigh": simscorehigh,
            "editdistmin": editdistmin,
            "editdistmax": editdistmax,
            "minmapq": minmapq,
            "lca_rank": lca_rank.value,  # important to get string
            "max_position": max_position,
            #
            "storage_path": storage_path,
            "cores": cores,
            "bayesian": bayesian,
            "debug": debug,
            #
            "paths": d_paths,
        }
    )

    with open(config_file, "w") as file:
        yaml.dump(config, file, sort_keys=False)


#%%


@cli_app.command(
    "compute",
    # context_settings={
    #     "allow_extra_args": True,
    #     "ignore_unknown_options": True,
    # },
)
def cli_compute(ctx: typer.Context):
    """Compute the LCA and Ancient Damage given the configuration."""

    if not config_file.exists():
        typer.echo("You have to run './metadamageprofiler.sh config' first.")
        raise typer.Abort()

    import yaml
    import subprocess

    with open(config_file, "r") as file:
        cores = yaml.safe_load(file)["cores"]

    typer.echo(__name__)
    # typer.echo(" ".join(commands))
    # subprocess.run(commands)


#%%


@cli_app.command("dashboard")
def cli_dashboard(
    results_dir: Path = typer.Argument(
        storage_path_default / "results",
        help="Directory contantaining the results of a previous run of metadamageprofiler.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Whether or not the debug-button should be displayed.",
    ),
    dashboard_port: int = typer.Option(
        8050,
        help="Dashboard port.",
    ),
    dashboard_host: str = typer.Option(
        "0.0.0.0",
        help="Dashboard host address",
    ),
):
    """Visualize the results in an interactive dashboard.

    run as e.g.:

    \b
        $ metadamageprofiler dashboard

    or for another directory than default:

    \b
        $ metadamageprofiler dashboard ./other/dir/results

    """

    from metadamageprofiler.dashboard import utils, app

    if not results_dir.exists():
        typer.echo("Please choose a valid directory")
        raise typer.Abort()

    if not debug:
        utils.open_browser_in_background()

    dashboard_app = app.get_app(results_dir)

    dashboard_app.run_server(
        debug=debug,
        host=dashboard_host,
        port=dashboard_port,
    )


#%%


@cli_app.command("clean")
def cli_clean():
    """Clean the current directory."""

    import subprocess
    import importlib_resources

    snakefile = str(importlib_resources.files("metadamageprofiler") / "Snakefile")
    commands = ["snakemake", "--snakefile", snakefile, "--unlock"]
    typer.echo(" ".join(commands))
    subprocess.run(commands)


#%%


def cli_main():
    cli_app(prog_name="metadamageprofiler")
