#%%
from pathlib import Path
from typing import Optional

import typer

from metaDMG.cli import cli_utils


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
    Welcome to metaDMG.

    First generate a config file::

        $ metaDMG config --help

    And then compute the ancient damage statistics::

        $ metaDMG compute --help

    And subsequently visualise the results using the dashboard::

        $ metaDMG dashboard --help

    """


#%%


@cli_app.command("config")
def create_config(
    samples: list[Path] = typer.Argument(
        ...,
        help="Single or multiple alignment-files (or a directory containing them).",
    ),
    names: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) names.dmp.gz.",
    ),
    nodes: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) nodes.dmp.gz.",
    ),
    acc2tax: Optional[Path] = typer.Option(
        None,
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
    bayesian: bool = typer.Option(
        False,
        "--bayesian",
        help="Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100.",
    ),
    forced: bool = typer.Option(
        False,
        "--forced",
        help="Forced computation (even though the files already exists)..",
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
    long_name: bool = typer.Option(
        False,
        "--long-name",
        help="Use the full name of the sample file as sample name..",
    ),
    damage_mode: cli_utils.DAMAGE_MODE = typer.Option(
        cli_utils.DAMAGE_MODE.LCA,
        case_sensitive=False,
        help="The Damage Mode. Use 'LCA' unless you know what you are doing.",
    ),
):
    """Generate the config file."""

    if (damage_mode.lower() == "lca") and (
        any(x is None for x in [names, nodes, acc2tax])
    ):
        typer.echo("--names, --nodes, and --acc2tax are mandatory when doing LCA.")
        raise typer.Exit(code=1)

    from metaDMG import utils

    config = utils.paths_to_strings(
        {
            "samples": utils.extract_alignments(
                samples,
                prefix=sample_prefix,
                suffix=sample_suffix,
                long_name=long_name,
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
            "forced": forced,
            "dir": storage_dir,
            "cores": cores,
            "cores_pr_fit": cores_pr_fit,
            "bayesian": bayesian,
            "config_path": str(config_path),
            "damage_mode": damage_mode.lower(),
        }
    )

    utils.save_config_file(config, config_path)


#%%


@cli_app.command("compute")
def compute(
    config_path: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    forced: bool = typer.Option(
        False,
        "--forced",
        help="Forced computation (even though the files already exists).",
    ),
):
    """Compute the LCA and Ancient Damage given the configuration file."""

    from metaDMG import utils

    utils.check_metaDMG_fit()

    from metaDMG.fit import (
        get_logger_port_and_path,
        make_configs,
        run_workflow,
        setup_logger,
    )

    log_port, log_path = get_logger_port_and_path()

    setup_logger(log_port=log_port, log_path=log_path)

    configs = make_configs(
        config_path=config_path,
        log_port=log_port,
        log_path=log_path,
        forced=forced,
    )

    run_workflow(configs)


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

    run as e.g.::

        $ metaDMG dashboard

    or for another config than default::

        $ metaDMG dashboard non-default-config.yaml --port 8050 --host 0.0.0.0 --debug

    """

    from metaDMG import utils

    utils.check_metaDMG_viz()

    from metaDMG.viz import start_dashboard

    results_dir = utils.get_results_dir(
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
    config_path: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
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
    add_fit_predictions: bool = typer.Option(
        False,
        help="Add fit predictions D(x) to the output",
    ),
):
    """Filter and save the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query=query,
        config_path=config_path,
        results_dir=results_dir,
        add_fit_predictions=add_fit_predictions,
    )


#%%


@cli_app.command("convert")
def convert(
    config_path: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
        None,
        help="Path to the results directory.",
    ),
    output: Path = typer.Option(
        ...,
        help="Where to save the converted file.",
    ),
    add_fit_predictions: bool = typer.Option(
        False,
        help="Add fit predictions D(x) to the output",
    ),
):
    """Convert the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query="",
        config_path=config_path,
        results_dir=results_dir,
        add_fit_predictions=add_fit_predictions,
    )


#%%


@cli_app.command("plot")
def plot(
    config_path: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
        None,
        help="Path to the results directory.",
    ),
    query: str = typer.Option(
        "",
        help="Filtering query",
    ),
    samples: str = typer.Option(
        "",
        help="Only use specific Tax IDs",
    ),
    tax_ids: str = typer.Option(
        "",
        help="Only use specific Tax IDs",
    ),
    pdf_out: Path = typer.Option(
        "pdf_export.pdf",
        file_okay=True,
        help="Output PDF file (pdf_export.pdf).",
    ),
):
    """Filter and save the results to either a combined csv or tsv file."""

    from metaDMG import utils

    utils.check_metaDMG_viz()

    from metaDMG.filters import filter_results
    from metaDMG.utils import get_results_dir
    from metaDMG.viz.figures import save_pdf_plots
    from metaDMG.viz.results import Results

    results_dir = get_results_dir(
        config_path=config_path,
        results_dir=results_dir,
    )

    results = Results(results_dir)

    if tax_ids:
        tax_ids_list = list(map(int, tax_ids.split(", ")))
        query += f" & tax_id in {tax_ids_list}"

    if samples:
        samples_list = samples.split(", ")
        query += f" & sample in {samples_list}"

    df_results = filter_results(results.df, query)

    save_pdf_plots(df_results, results, pdf_path=pdf_out, do_tqdm=True)  # type: ignore


#%%


@cli_app.command("mismatch-to-mapDamage")
def mismatch_to_mapDamage(
    filename: Path = typer.Argument(
        ...,
        file_okay=True,
        help="Path to the config-file.",
    ),
    csv_out: Path = typer.Option(
        "misincorporation.txt",
        file_okay=True,
        help="Output CSV file (misincorporation.txt).",
    ),
):
    """Convert the mismatch file to mapDamage misincorporation.txt format."""

    from metaDMG import utils

    utils.check_metaDMG_fit()

    from metaDMG.fit import mismatch_to_mapDamage

    mismatch_to_mapDamage.convert(filename=filename, csv_out=csv_out)


#%%

# needed for sphinx documentation
typer_click_object = typer.main.get_command(cli_app)


def cli_main():
    cli_app(prog_name="metaDMG")