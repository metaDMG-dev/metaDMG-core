import typer
from pathlib import Path
from typing import List, Optional

from metaDMG import cli_utils

cli_app = cli_utils.get_cli_app()

storage_dir_default = Path("./data/")
results_dir_default = storage_dir_default / "results"
config_path_default = Path("config.yaml")

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

    And subsequently visualise the results using the dashboard:

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
    metaDMG_cpp: str = typer.Option(
        "./metaDMG-cpp",
        help="The command needed to run the metaDMG-lca program.",
    ),
    simscorelow: float = typer.Option(
        0.95,
        help="Normalised edit distance (read to reference similarity) minimum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 1),
    ),
    simscorehigh: float = typer.Option(
        1.0,
        help="Normalised edit distance (read to reference similarity) maximum. Number between 0-1.",
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
        help="Number of positions to include (|x| < max_position).",
    ),
    weighttype: int = typer.Option(
        1,
        help="Method for calculating weights",
    ),
    fix_ncbi: int = typer.Option(
        1,
        help="Fix the (ncbi) database. Disable if using a custom database.",
    ),
    lca_rank: cli_utils.RANKS = typer.Option(
        cli_utils.RANKS.none,
        case_sensitive=False,
        help="The LCA rank used in ngsLCA.",
    ),
    forward_only: bool = typer.Option(
        False,
        "--forward-only",
        help="Only use the forward direction.",
    ),
    storage_dir: Path = typer.Option(
        storage_dir_default,
        help="Path where the generated output files and folders are stored.",
    ),
    cores: int = typer.Option(
        1,
        help="The maximum number of cores to use in the ancient damage estimation.",
    ),
    cores_pr_fit: int = typer.Option(
        1,
        help="Number of cores pr. fit. Do not change unless you know what you are doing.",
    ),
    config_path: Path = typer.Option(
        config_path_default,
        help="The name of the config file. ",
    ),
    sample_prefix: str = typer.Option(
        "",
        help="Prefix for the sample names.",
    ),
    sample_suffix: str = typer.Option(
        "",
        help="Suffix for the sample names.",
    ),
    bayesian: bool = typer.Option(
        False,
        "--bayesian",
        help="Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100.",
    ),
):
    """Generate the config file."""

    import yaml
    from metaDMG import utils

    config = utils.remove_paths(
        {
            "samples": utils.extract_alignments(
                samples, prefix=sample_prefix, suffix=sample_suffix
            ),
            #
            "metaDMG-lca": metaDMG_cpp,
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
            "weighttype": weighttype,
            "fix_ncbi": fix_ncbi,
            "forward_only": forward_only,
            #
            "dir": storage_dir,
            "cores": cores,
            "cores_pr_fit": cores_pr_fit,
            "bayesian": bayesian,
            "config_path": str(config_path),
        }
    )

    with open(config_path, "w") as file:
        yaml.dump(config, file, sort_keys=False)


#%%


@cli_app.command("compute")
def compute(
    config_path: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
):
    """Compute the LCA and Ancient Damage given the configuration file."""

    from metaDMG import utils
    from metaDMG.fit import run_workflow, get_logger_port_and_path, setup_logger

    log_port, log_path = get_logger_port_and_path()

    setup_logger(log_port=log_port, log_path=log_path)

    config = utils.load_config(
        config_path=config_path,
        log_port=log_port,
        log_path=log_path,
    )

    run_workflow(config)


#%%


@cli_app.command("dashboard")
def dashboard(
    config_path: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results: Optional[Path] = typer.Option(
        None,
        help="Path to the results directory.",
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
    """Visualise the results in an interactive dashboard.
    Requires metaDMG-viz to be installed.

    run as e.g.:

    \b
        $ metaDMG dashboard

    or for another config than default:

    \b
        $ metaDMG dashboard non-default-config.yaml --port 8050 --host 0.0.0.0

    """

    try:
        from metaDMG_viz import start_dashboard
    except ModuleNotFoundError:
        print("""metaDMG-viz has to be installed: pip install "metaDMG[all]" """)
        typer.Abort()

    from metaDMG.utils import get_results_dir

    results_dir = get_results_dir(
        config_path=config_path,
        results_dir=results,
    )

    start_dashboard(
        results_dir=results_dir,
        debug=debug,
        host=host,
        port=port,
    )


#%%


@cli_app.command("filter")
def filter(
    config: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results: Optional[Path] = typer.Option(
        None,
        help="Path to the results directory.",
    ),
    output: Path = typer.Option(
        ...,
        help="Where to save the converted file.",
    ),
    query: str = typer.Option(
        "",
        help="Filtering query",
    ),
):
    """Filter and save the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query=query,
        config_path=config,
        results_dir=results,
    )


#%%


@cli_app.command("convert")
def convert(
    config: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results: Optional[Path] = typer.Option(
        None,
        help="Path to the results directory.",
    ),
    output: Path = typer.Option(
        ...,
        help="Where to save the converted file.",
    ),
):
    """Convert the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query="",
        config_path=config,
        results_dir=results,
    )


#%%


def cli_main():
    cli_app(prog_name="metaDMG")
