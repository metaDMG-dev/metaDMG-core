import typer
from pathlib import Path
from typing import List, Optional

from metaDMG import utils, cli_utils

cli_app = cli_utils.get_cli_app()

storage_dir_default = Path("./data/")
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
    metaDMG.

    First run the LCA and compute the ancient damage statistics with the 'compute' command:

    \b
        $ metaDMG config --help

    \b
        $ metaDMG compute --help

    And subsequently visualize the results using the dashboard:

    \b
        $ metaDMG dashboard --help

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
    metaDMG_lca: str = typer.Option(
        "./metaDMG-lca",
        help="The command needed to run the metaDMG-lca program.",
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
    storage_dir: Path = typer.Option(
        storage_dir_default,
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
):
    """Generate the config file."""

    import yaml

    config = utils.remove_paths(
        {
            "samples": utils.extract_alignments(samples),
            #
            "metaDMG-lca": metaDMG_lca,
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
            "dir": storage_dir,
            "cores": cores,
            "bayesian": bayesian,
        }
    )

    with open(config_file, "w") as file:
        yaml.dump(config, file, sort_keys=False)


#%%


@cli_app.command("compute")
def compute(
    config: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to the config-file.",
    ),
):
    """Compute the LCA and Ancient Damage given the configuration."""

    from metaDMG import utils
    from metaDMG_fit import run_workflow

    run_workflow(config=config)


#%%


@cli_app.command("dashboard")
def cli_dashboard(
    config: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        help="Path to the config-file.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Whether or not the debug-button should be displayed.",
    ),
    port: int = typer.Option(
        8050,
        help="Dashboard port.",
    ),
    host: str = typer.Option(
        "0.0.0.0",
        help="Dashboard host address",
    ),
):
    """Visualize the results in an interactive dashboard.

    run as e.g.:

    \b
        $ metaDMG dashboard

    or for another config than default:

    \b
        $ metaDMG dashboard ./some/other/dir/config2.yaml

    """

    from metaDMG_viz import start_dashboard

    start_dashboard(
        config=config,
        debug=debug,
        host=host,
        port=port,
    )


#%%

def cli_main():
    cli_app(prog_name="metaDMG")
