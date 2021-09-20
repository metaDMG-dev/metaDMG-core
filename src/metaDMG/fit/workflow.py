# from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor as Pool
from logger_tt import logger
from datetime import datetime
from metaDMG.fit import serial, fit_utils
from metaDMG.utils import check_number_of_jobs


def run_workflow(config):

    configs = fit_utils.make_configs(config)

    cores = config["cores"]

    logger.info(f"Running metaDMG on {len(configs)} files in total.")

    if cores == 1 or len(configs) == 1:
        logger.info(f"Running in seriel (1 core)")
        for config in configs:
            dfs = serial.run_single_config(config)
            df_mismatches, df_fit_results, df_results = dfs

    else:
        logger.info(f"Running with {cores} processes in parallel")
        check_number_of_jobs(config)

        with Pool(max_workers=cores) as pool:
            # for dfs in pool.imap_unordered(serial.run_single_config, configs):
            for dfs in pool.map(serial.run_single_config, configs):
                df_mismatches, df_fit_results, df_results = dfs
