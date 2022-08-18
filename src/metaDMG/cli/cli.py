#%%
from pathlib import Path
from typing import Optional, Union

import typer
from rich import print

from metaDMG.cli import cli_utils


cli_app = cli_utils.get_cli_app()


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
        help="Path to the (NCBI) names-mdmg.dmp.",
        rich_help_panel="LCA parameters",
    ),
    nodes: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) nodes-mdmg.dmp.",
        rich_help_panel="LCA parameters",
    ),
    acc2tax: Optional[Path] = typer.Option(
        None,
        exists=True,
        file_okay=True,
        help="Path to the (NCBI) acc2tax.gz.",
        rich_help_panel="LCA parameters",
    ),
    min_similarity_score: Optional[float] = typer.Option(
        None,
        "--min-similarity-score",
        "-s",
        help="Normalised edit distance (read to reference similarity) minimum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range_or_None(x, 0, 1),
        rich_help_panel="LCA parameters",
    ),
    max_similarity_score: Optional[float] = typer.Option(
        None,
        "--max-similarity-score",
        "-S",
        help="Normalised edit distance (read to reference similarity) maximum. Number between 0-1.",
        callback=lambda x: cli_utils.is_in_range_or_None(x, 0, 1),
        rich_help_panel="LCA parameters",
    ),
    min_edit_dist: Optional[int] = typer.Option(
        None,
        # 0,
        "--min-edit-dist",
        "-e",
        help="Minimum edit distance (read to reference similarity). Positive integer.",
        callback=lambda x: cli_utils.is_positive_int_or_None(x),
        rich_help_panel="LCA parameters",
    ),
    max_edit_dist: Optional[int] = typer.Option(
        None,
        # 10,
        "--max-edit-dist",
        "-E",
        help="Maximum edit distance (read to reference similarity). Positive integer.",
        callback=lambda x: cli_utils.is_positive_int_or_None(x),
        rich_help_panel="LCA parameters",
    ),
    min_mapping_quality: int = typer.Option(
        0,
        "--min-mapping-quality",
        "-q",
        help="Minimum mapping quality.",
        rich_help_panel="LCA parameters",
    ),
    custom_database: bool = typer.Option(
        False,
        "--custom-database",
        "-u",
        help="Fix the (ncbi) database. Disable if using a custom database.",
        rich_help_panel="LCA parameters",
    ),
    lca_rank: cli_utils.RANKS = typer.Option(
        cli_utils.RANKS.none,
        "--lca-rank",
        "-r",
        case_sensitive=False,
        help="The LCA rank used in ngsLCA.",
        rich_help_panel="LCA parameters",
    ),
    # GENERAL PARAMETERS
    metaDMG_cpp: str = typer.Option(
        "./metaDMG-cpp",
        "--metaDMG-cpp",
        "-m",
        help="The command needed to run the metaDMG-cpp program.",
        rich_help_panel="General parameters",
    ),
    max_position: int = typer.Option(
        15,
        "--max-position",
        "-P",
        help="Number of positions to include (|x| < max_position).",
        rich_help_panel="General parameters",
    ),
    min_reads: int = typer.Option(
        0,
        "--min-reads",
        "-n",
        help="Minimum number of reads to include in the fits (min_reads <= N_reads).",
        rich_help_panel="General parameters",
    ),
    weight_type: int = typer.Option(
        1,
        "--weight-type",
        "-w",
        help="Method for calculating weights",
        rich_help_panel="General parameters",
    ),
    forward_only: bool = typer.Option(
        False,
        "--forward-only",
        "-l",
        help="Only use the forward direction.",
        rich_help_panel="General parameters",
    ),
    bayesian: bool = typer.Option(
        False,
        "--bayesian",
        "-b",
        help="Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100.",
        rich_help_panel="General parameters",
    ),
    output_dir: Path = typer.Option(
        cli_utils.output_dir_default,
        "--output-dir",
        "-o",
        help="Path where the generated output files and folders are stored.",
        rich_help_panel="General parameters",
    ),
    parallel_samples: int = typer.Option(
        1,
        "--parallel-samples",
        "-j",
        help="The number of samples to run in parallel. Default is running in seriel.",
        rich_help_panel="General parameters",
    ),
    cores_per_sample: int = typer.Option(
        1,
        "--cores-per-sample",
        "-i",
        help="Number of cores to use pr. sample. ",
        rich_help_panel="General parameters",
    ),
    config_file: Path = typer.Option(
        cli_utils.config_file_default,
        "--config-file",
        "-c",
        help="The name of the config file. ",
        rich_help_panel="General parameters",
    ),
    sample_prefix: str = typer.Option(
        "",
        help="Prefix for the sample names.",
        rich_help_panel="General parameters",
    ),
    sample_suffix: str = typer.Option(
        "",
        help="Suffix for the sample names.",
        rich_help_panel="General parameters",
    ),
    long_name: bool = typer.Option(
        False,
        "--long-name",
        help="Use the full name of the sample file as sample name..",
        rich_help_panel="General parameters",
    ),
    damage_mode: cli_utils.DAMAGE_MODE = typer.Option(
        cli_utils.DAMAGE_MODE.LCA,
        "--damage-mode",
        "-d",
        case_sensitive=False,
        help="The Damage Mode. Use 'LCA' unless you know what you are doing.",
        rich_help_panel="General parameters",
    ),
    overwrite_config: bool = typer.Option(
        False,
        "--overwrite",
        "-f",
        help="Overwrite config file without user confirmation.",
        rich_help_panel="General parameters",
    ),
):
    """Generate the config file."""

    if (damage_mode.lower() == "lca") and (
        any(x is None for x in [names, nodes, acc2tax])
    ):
        print(
            "[red]--names[/red], [red]--nodes[/red], and [red]--acc2tax[/red] "
            "are mandatory when doing LCA. \n"
            "If you do not want to perform LCA, set [green]--damage-mode[/green] "
            "to [green]LOCAL[/green] or [green]GLOBAL[/green]."
        )
        raise typer.Exit(code=1)

    from metaDMG import __version__

    config = cli_utils.get_config_dict(
        samples=samples,
        names=names,
        nodes=nodes,
        acc2tax=acc2tax,
        min_similarity_score=min_similarity_score,
        max_similarity_score=max_similarity_score,
        min_edit_dist=min_edit_dist,
        max_edit_dist=max_edit_dist,
        min_mapping_quality=min_mapping_quality,
        custom_database=custom_database,
        lca_rank=lca_rank,
        metaDMG_cpp=metaDMG_cpp,
        max_position=max_position,
        min_reads=min_reads,
        weight_type=weight_type,
        forward_only=forward_only,
        bayesian=bayesian,
        output_dir=output_dir,
        parallel_samples=parallel_samples,
        cores_per_sample=cores_per_sample,
        config_file=config_file,
        sample_prefix=sample_prefix,
        sample_suffix=sample_suffix,
        long_name=long_name,
        damage_mode=damage_mode,
        __version__=__version__,
    )

    cli_utils.save_config_file(config, config_file, overwrite_config)


#%%


@cli_app.command("config-gui")
def create_config_gui():
    """Generate the config file via a simple GUI."""

    from metaDMG.cli import cli_gui

    gui = cli_gui.Gui(verbose=True)
    gui.mainloop()


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

    from metaDMG.fit import get_logger_port_and_path, run_workflow, setup_logger

    log_port, log_path = get_logger_port_and_path()
    setup_logger(log_port=log_port, log_path=log_path)

    configs = utils.make_configs(
        config_file=config_file,
        log_port=log_port,
        log_path=log_path,
        force=force,
    )

    return_code = run_workflow(configs)
    if return_code != 0:
        raise typer.Exit(return_code)


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
    server: bool = typer.Option(
        False,
        "--server",
        "-s",
        help="Whether or not it is running on a server.",
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
        server=server,
        host=host,
        port=port,
    )


#%%


@cli_app.command("convert", rich_help_panel="Utils")
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


@cli_app.command("filter", rich_help_panel="Utils")
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


@cli_app.command("plot", rich_help_panel="Utils")
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


@cli_app.command("get-data", rich_help_panel="Utils")
def get_data(
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        "-o",
        help="Path to the output directory.",
    ),
):
    """Get test data and save it in the output-dir. Useful for e.g. the online tutorial."""

    from metaDMG.data import get_data

    get_data(output_dir=output_dir)


#%%


@cli_app.command("mismatch-to-mapDamage", rich_help_panel="Utils")
def mismatch_to_mapDamage(
    filename: Path = typer.Argument(
        ...,
        file_okay=True,
        help="Path to the mismatch-file to convert.",
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


@cli_app.command("PMD", rich_help_panel="Utils")
def PMD(
    filename: Path = typer.Argument(
        ...,
        file_okay=True,
        help="Path to the alignment file.",
    ),
    csv_out: Path = typer.Option(
        ...,
        "--output",
        "-o",
        file_okay=True,
        help="Output CSV file.",
    ),
    metaDMG_cpp: str = typer.Option(
        "./metaDMG-cpp",
        "--metaDMG-cpp",
        "-m",
        help="The command needed to run the metaDMG-cpp program.",
    ),
):
    """Compute the PMD scores for the chosen BAM file and save to csv."""

    from metaDMG.PMD import compute_PMDs

    df_PMDs = compute_PMDs(filename, metaDMG_cpp)

    csv_out.parent.mkdir(parents=True, exist_ok=True)
    df_PMDs.to_csv(csv_out, index=False)


#%%

# needed for sphinx documentation
typer_click_object = typer.main.get_command(cli_app)


def cli_main():
    cli_app(prog_name="metaDMG")
