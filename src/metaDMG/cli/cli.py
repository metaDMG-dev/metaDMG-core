#%%
from pathlib import Path
from typing import Optional

import typer

from metaDMG.cli import cli_utils


cli_app = cli_utils.get_cli_app()

output_dir_default = Path("./data/")
results_dir_default = output_dir_default / "results"
config_file_default = Path("config.yaml")

#%%


@cli_app.callback()
def callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
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
    # LCA parameters
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
    min_similarity_score: float = typer.Option(
        0.95,
        "--min-similarity-score",
        "-s",
        help="Normalised edit distance (read to reference similarity) minimum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 1),
    ),
    max_similarity_score: float = typer.Option(
        1.0,
        "--max-similarity-score",
        "-S",
        help="Normalised edit distance (read to reference similarity) maximum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 1),
    ),
    min_edit_dist: int = typer.Option(
        0,
        "--min-edit-dist",
        "-e",
        help="Minimum edit distance (read to reference similarity). Number between 0-10.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 10),
    ),
    max_edit_dist: int = typer.Option(
        10,
        "--max-edit-dist",
        "-E",
        help="Maximum edit distance (read to reference similarity). Number between 0-10.",
        callback=lambda x: cli_utils.is_in_range(x, 0, 10),
    ),
    min_mapping_quality: int = typer.Option(
        0,
        "--min-mapping-quality",
        "-q",
        help="Minimum mapping quality.",
    ),
    custom_database: bool = typer.Option(
        False,
        "--custom-database",
        "-u",
        help="Fix the (ncbi) database. Disable if using a custom database.",
    ),
    lca_rank: cli_utils.RANKS = typer.Option(
        cli_utils.RANKS.none,
        "--lca-rank",
        "-r",
        case_sensitive=False,
        help="The LCA rank used in ngsLCA.",
    ),
    # GENERAL PARAMETERS
    metaDMG_cpp: str = typer.Option(
        "./metaDMG-cpp",
        "--metaDMG-cpp",
        "-m",
        help="The command needed to run the metaDMG-cpp program.",
    ),
    max_position: int = typer.Option(
        15,
        "--max-position",
        "-P",
        help="Number of positions to include (|x| < max_position).",
    ),
    weight_type: int = typer.Option(
        1,
        "--weight-type",
        "-w",
        help="Method for calculating weights",
    ),
    forward_only: bool = typer.Option(
        False,
        "--forward-only",
        "-l",
        help="Only use the forward direction.",
    ),
    bayesian: bool = typer.Option(
        False,
        "--bayesian",
        "-b",
        help="Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100.",
    ),
    output_dir: Path = typer.Option(
        output_dir_default,
        "--output-dir",
        "-o",
        help="Path where the generated output files and folders are stored.",
    ),
    parallel_samples: int = typer.Option(
        1,
        "--parallel-samples",
        "-j",
        help="The number of samples to run in parallel. Default is running in seriel.",
    ),
    cores_per_sample: int = typer.Option(
        1,
        "--cores-per-sample",
        "-i",
        help="Number of cores to use pr. sample. ",
    ),
    config_file: Path = typer.Option(
        config_file_default,
        "--config-file",
        "-c",
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
        "--damage-mode",
        "-d",
        case_sensitive=False,
        help="The Damage Mode. Use 'LCA' unless you know what you are doing.",
    ),
    overwrite_config: bool = typer.Option(
        False,
        "--overwrite",
        "-f",
        help="Overwrite config file without user confirmation.",
    ),
):
    """Generate the config file."""

    if (damage_mode.lower() == "lca") and (
        any(x is None for x in [names, nodes, acc2tax])
    ):
        typer.echo("--names, --nodes, and --acc2tax are mandatory when doing LCA.")
        raise typer.Exit(code=1)

    from metaDMG import __version__, utils

    config = utils.paths_to_strings(
        {
            "samples": utils.extract_samples(
                samples,
                prefix=sample_prefix,
                suffix=sample_suffix,
                long_name=long_name,
            ),
            #
            "metaDMG_cpp": metaDMG_cpp,
            "names": names,
            "nodes": nodes,
            "acc2tax": acc2tax,
            "min_similarity_score": min_similarity_score,
            "max_similarity_score": max_similarity_score,
            "min_edit_dist": min_edit_dist,
            "max_edit_dist": max_edit_dist,
            "min_mapping_quality": min_mapping_quality,
            "lca_rank": lca_rank.value,  # important to get string
            "max_position": max_position,
            "weight_type": weight_type,
            "custom_database": custom_database,
            "forward_only": forward_only,
            #
            "output_dir": output_dir,
            "parallel_samples": parallel_samples,
            "cores_per_sample": cores_per_sample,
            "bayesian": bayesian,
            "config_file": str(config_file),
            "damage_mode": damage_mode.lower(),
            "version": __version__,
        }
    )

    utils.save_config_file(config, config_file, overwrite_config)


#%%


@cli_app.command("compute")
def compute(
    config_file: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
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
        config_file=config_file,
        log_port=log_port,
        log_path=log_path,
        force=force,
    )

    run_workflow(configs)


#%%


@cli_app.command("dashboard")
def dashboard(
    config_file: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results: Optional[Path] = typer.Option(
        None,
        "--results",
        "-r",
        help="Path to the results directory.",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Whether or not the debug-button should be displayed.",
    ),
    port: int = typer.Option(
        8050,
        "--port",
        "-p",
        help="Dashboard port.",
    ),
    host: str = typer.Option(
        "0.0.0.0",
        "--host",
        "-h",
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
        config_file=config_file,
        results_dir=results,
    )

    start_dashboard(
        results_dir=results_dir,
        debug=debug,
        host=host,
        port=port,
    )


#%%


@cli_app.command("convert")
def convert(
    config_file: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
        None,
        "--results",
        "-r",
        help="Path to the results directory.",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Where to save the converted file.",
    ),
    add_fit_predictions: bool = typer.Option(
        False,
        "--add-fit-predictions",
        "-a",
        help="Add fit predictions D(x) to the output",
    ),
):
    """Convert the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query="",
        config_file=config_file,
        results_dir=results_dir,
        add_fit_predictions=add_fit_predictions,
    )


#%%


@cli_app.command("filter")
def filter(
    config_file: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
        None,
        "--results",
        "-r",
        help="Path to the results directory.",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="Where to save the converted file.",
    ),
    query: str = typer.Option(
        "",
        "--query",
        "-q",
        help="Filtering query",
    ),
    add_fit_predictions: bool = typer.Option(
        False,
        "--add-fit-predictions",
        "-a",
        help="Add fit predictions D(x) to the output",
    ),
):
    """Filter and save the results to either a combined csv or tsv file."""

    from metaDMG.filters import filter_and_save_results

    filter_and_save_results(
        output=output,
        query=query,
        config_file=config_file,
        results_dir=results_dir,
        add_fit_predictions=add_fit_predictions,
    )


#%%


@cli_app.command("plot")
def plot(
    config_file: Optional[Path] = typer.Argument(
        None,
        file_okay=True,
        help="Path to the config-file.",
    ),
    results_dir: Optional[Path] = typer.Option(
        None,
        "--results",
        "-r",
        help="Path to the results directory.",
    ),
    query: str = typer.Option(
        "",
        "--query",
        "-q",
        help="Filtering query",
    ),
    samples: str = typer.Option(
        "",
        "--samples",
        "-s",
        help="Only use specific Tax samples",
    ),
    tax_ids: str = typer.Option(
        "",
        "--tax-ids",
        "-t",
        help="""Only use specific Tax IDs. Example: "" """,
    ),
    pdf_out: Path = typer.Option(
        "pdf_export.pdf",
        "--output",
        "-o",
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
    from metaDMG.viz.results import VizResults

    results_dir = get_results_dir(
        config_file=config_file,
        results_dir=results_dir,
    )

    viz_results = VizResults(results_dir)

    if tax_ids:
        tax_ids_list = utils.split_string(tax_ids)
        query += f" & tax_id in {tax_ids_list}"

    if samples:
        samples_list = utils.split_string(samples)
        query += f" & sample in {samples_list}"

    df_results = filter_results(viz_results.df, query)

    save_pdf_plots(df_results, viz_results, pdf_path=pdf_out, do_tqdm=True)  # type: ignore


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
        "--output",
        "-o",
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
