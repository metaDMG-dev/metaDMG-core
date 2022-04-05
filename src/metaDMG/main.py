from pathlib import Path
from typing import Optional

from metaDMG.filters import load_results


# Needed for sphinx to include load_results
__all__ = ["compute_config", "run_dashboard", "load_results"]


def compute_config(
    config_file: Path = Path("config.yaml"),
    force: bool = False,
) -> None:
    """Run the LCA and fit on the config file.

    Parameters
    ----------
    config_file
        The config file to run the computations on, by default Path("config.yaml")
    force
        Force the computation, i.e. do not load (intermediate) results, by default False
    """

    from metaDMG import utils

    utils.check_metaDMG_fit()

    from metaDMG.fit import run_workflow

    configs = utils.make_configs(config_file=config_file, force=force)

    run_workflow(configs)


def run_dashboard(
    config_file: Path = Path("config.yaml"),
    results: Optional[Path] = None,
    debug: bool = False,
    server: bool = False,
    port: int = 8050,
    host: str = "0.0.0.0",
) -> None:
    """Visualise the results in an interactive dashboard

    Parameters
    ----------
    config_file
        The the config file to use to locate the results directory, by default Path("config.yaml")
    results
        The results directory, by default None
    debug
        Whether or not the debug-button should be displayed, by default False
    server
        Whether or not it should behave as running on a server, by default False
    port
        Dashboard port, by default 8050
    host
        Dashboard host address, by default "0.0.0.0"
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
