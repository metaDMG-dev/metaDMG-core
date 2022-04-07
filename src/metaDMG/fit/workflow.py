#%%
import filecmp
import shutil
from concurrent.futures import ProcessPoolExecutor as Pool
from datetime import datetime
from multiprocessing import current_process

from logger_tt import logger

from metaDMG.fit.serial import run_single_config
from metaDMG.utils import Configs


#%%


def data_dir_is_ok(configs: Configs, force: bool = False) -> bool:
    """Check if the output_dir is ok. I.e. whether or not another config file
    already exists, and if it does, whether or not it is identical to the current one.
    Does not allow overwriting of previous runs unless `--force` is used.

    Parameters
    ----------
    configs
        _description_
    force, optional
        _description_, by default False

    Returns
    -------
        _description_
    """
    yamls = list(configs["output_dir"].glob("*.yaml"))
    ymls = list(configs["output_dir"].glob("*.yml"))
    other_configs = yamls + ymls

    if len(other_configs) == 0:
        return True

    is_identical = filecmp.cmp(
        configs["config_file"],
        other_configs[0],
        shallow=False,
    )

    if is_identical:
        return True

    if force:
        return True

    s = (
        "You are trying to save data to a directory which "
        "is already used with another config file. "
        "Use 'metaDMG compute [...] --force' if you know what you are doing."
    )

    logger.warning(s)

    return False


#%%


def copy_config_file(configs: Configs) -> None:
    """Copy config file to output_dir.

    Parameters
    ----------
    config
        A single configuration
    """
    config_file_out = configs["output_dir"] / configs["config_file"]
    if not config_file_out.is_file():

        current_process().name = str(configs["config_file"])
        logger.info(f"Copying config file to {config_file_out}.")

        shutil.copy(configs["config_file"], config_file_out)


#%%


def run_workflow(configs: Configs) -> None:

    if not data_dir_is_ok(configs, force=configs["force"]):
        return

    parallel_samples = min(configs["parallel_samples"], len(configs))
    logger.info(f"Running metaDMG on {len(configs)} configs in total.")

    if parallel_samples == 1 or len(configs) == 1:
        logger.info(f"Running in serial (1 core)")
        for config in configs:
            dfs = run_single_config(config)
            # df_mismatches, df_fit_results, df_results = dfs

    else:
        logger.info(f"Running with {parallel_samples} processes in parallel")
        configs.check_number_of_jobs()

        with Pool(max_workers=parallel_samples) as pool:
            # for dfs in pool.imap_unordered(serial.run_single_config, configs):
            for dfs in pool.map(run_single_config, configs):
                pass
                # df_mismatches, df_fit_results, df_results = dfs

    copy_config_file(configs)
