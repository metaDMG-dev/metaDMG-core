# from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor as Pool
from datetime import datetime
from multiprocessing import current_process

from logger_tt import logger

from metaDMG.fit.serial import run_single_config_count_errors
from metaDMG.utils import Configs


def run_workflow(configs: Configs) -> int:
    """Runs the entire metaDMG workflow.

    Parameters
    ----------
    configs
        A Configs object containing the configuration parameters for the workflow.

    Returns
    -------
        _description_
    """

    parallel_samples = min(configs["parallel_samples"], len(configs))

    logger.info(f"Running metaDMG on {len(configs)} files in total.")

    N_errors = 0

    if parallel_samples == 1 or len(configs) == 1:
        N = configs["cores_per_sample"]
        s = f"Running the samples in serial (sequentially), each using {N} core(s)."
        logger.info(s)
        for config in configs:
            N_errors += run_single_config_count_errors(config)

    else:
        logger.info(f"Running with {parallel_samples} processes in parallel")
        configs.check_number_of_jobs()

        with Pool(max_workers=parallel_samples) as pool:
            for n_error in pool.map(run_single_config_count_errors, configs):
                N_errors += n_error

    # set back the name of the process to the original name
    current_process().name = "MainProcess"

    if N_errors > 0:
        logger.error(f"{N_errors} error(s) occurred during the computation.")

    return N_errors
