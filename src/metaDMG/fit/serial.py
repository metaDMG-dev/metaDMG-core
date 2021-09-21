import pandas as pd
from pathlib import Path
import subprocess
import shlex
import shutil
from logger_tt import logger
from multiprocessing import current_process
import json
from metaDMG.loggers.loggers import setup_logger
from metaDMG.fit import mismatches, fits, results

#%%


def do_run(targets, forced=False):

    if forced:
        return True

    if not isinstance(targets, list):
        targets = [targets]

    if all(Path(target).exists() for target in targets):
        return False
    else:
        return True


def do_load(targets, forced=False):
    return not do_run(targets, forced=forced)


def data_dir(config, name, suffix="parquet"):
    target = Path(config["dir"]) / name / f"{config['sample']}.{name}.{suffix}"
    return str(target)


#%%


def get_LCA_command(config):
    sample = config["sample"]
    bam = config["samples"][sample]
    lca_rank = f"-lca_rank {config['lca_rank']}" if config["lca_rank"] != "" else ""

    command = (
        f"{config['metaDMG-lca']} lca "
        f"-bam {bam} "
        f"-outnames {sample} "
        f"-names {config['names']} "
        f"-nodes {config['nodes']} "
        f"-acc2tax {config['acc2tax']} "
        f"-simscorelow {config['simscorelow']} "
        f"-simscorehigh {config['simscorehigh']} "
        f"-editdistmin {config['editdistmin']} "
        f"-editdistmax {config['editdistmax']} "
        f"{lca_rank} "
        f"-minmapq {config['minmapq']} "
        f"-howmany {config['max_position']} "
        f"-weighttype {config['weighttype']} "
        f"-fix_ncbi {config['fix_ncbi']} "
    )
    return command


def get_LCA_mismatches_command(config):
    sample = config["sample"]
    bdamage = f"{sample}.bdamage.gz"
    lca_stat = f"{sample}.lca.stat"

    command = (
        f"{config['metaDMG-lca']} print_ugly "
        f"{bdamage} "
        f"-names {config['names']} "
        f"-nodes {config['nodes']} "
        f"-lcastat {lca_stat} "
    )
    return command


def run_command(command):

    p = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in iter(p.stdout.readline, b""):
        if line:
            line = line.decode("utf-8")
            if line.endswith("\n"):
                line = line[:-1]
            yield line


def move_files(config):
    sample = config["sample"]

    d_move_source_target = {
        f"{sample}.bdamage.gz.uglyprint.mismatch.txt": config["path_mismatches_txt"],
        f"{sample}.bdamage.gz.uglyprint.stat.txt": config["path_mismatches_stat"],
        f"{sample}.lca": config["path_lca"],
    }
    for source_path, target_path in d_move_source_target.items():
        logger.debug(f"Moving {source_path} to {target_path}.")
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source_path, target_path)


def delete_files(config):
    sample = config["sample"]

    bam = Path(config["samples"][sample]).stem  # .name

    paths_to_remove = [
        f"{sample}.lca.stat",
        f"{sample}.bdamage.gz",
        f"{sample}.log",
        *list(Path(".").glob(f"*{bam}*.bam.bin")),
    ]
    for path in paths_to_remove:
        logger.debug(f"Removing {path}.")
        Path(path).unlink()


def run_LCA(config, forced=False):

    logger.info(f"Getting LCA.")

    targets = [
        config["path_mismatches_txt"],
        config["path_mismatches_stat"],
        config["path_lca"],
    ]

    if do_run(targets, forced=forced):

        logger.info(f"LCA has to be computed. " "This can take a while, please wait.")

        command_LCA = get_LCA_command(config)
        command_LCA_mismatches = get_LCA_mismatches_command(config)

        for line in run_command(command_LCA):
            logger.debug(line)
        for line in run_command(command_LCA_mismatches):
            logger.debug(line)

        move_files(config)
        delete_files(config)

    else:
        logger.info(f"LCA already been run before.")


#%%


def get_df_mismatches(config, forced=False):

    logger.info(f"Getting df_mismatches")

    target = data_dir(config, name="mismatches")

    if do_run(target, forced=forced):
        logger.info(f"Computing df_mismatches.")
        df_mismatches = mismatches.compute(config)
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        df_mismatches.to_parquet(target)

    else:
        logger.info(f"Loading df_mismatches.")
        df_mismatches = pd.read_parquet(target)

    return df_mismatches


#%%


def dataframe_columns_contains(df, s):
    return any(s in column for column in df.columns)


def get_df_fit_results(config, df_mismatches, forced=False):

    logger.info(f"Getting df_fit_results.")

    target = data_dir(config, name="fit_results")

    if do_load(target, forced=forced):
        logger.info(f"Try to load df_fit_results.")
        df_fit_results = pd.read_parquet(target)

        # if frequentist fits only, return immediately
        if not config["bayesian"]:
            logger.info(f"Loading df_fit_results (frequentist).")
            return df_fit_results

        # if df_fit_results has already been run with Bayesian, return this
        if dataframe_columns_contains(df_fit_results, "Bayesian"):
            logger.info(f"Loading df_fit_results (Bayesian).")
            return df_fit_results

    # Compute the fits
    info = "Fitting the data"
    if config["bayesian"]:
        info += " with a Bayesian model, please wait."
    else:
        info += " with a frequentist (MAP) model."

    logger.info(info)
    df_fit_results = fits.compute(config, df_mismatches)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    df_fit_results.to_parquet(target)

    return df_fit_results


#%%


def get_df_results(config, df_mismatches, df_fit_results, forced=False):

    logger.info(f"Getting df_results.")

    target = data_dir(config, name="results")

    if do_load(target, forced=forced):
        logger.info(f"Loading df_results.")
        df_results = pd.read_parquet(target)

        # if frequentist fits only, return immediately
        if not config["bayesian"]:
            return df_results

        # if df_results has already been run with Bayesian, return this
        if dataframe_columns_contains(df_results, "Bayesian"):
            return df_results

    # Compute the results:
    logger.info(f"Computing df_results.")
    df_results = results.merge(df_mismatches, df_fit_results)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    df_results.to_parquet(target)

    return df_results


#%%


class DB:
    def __init__(self, path):
        self.path = path

    def save(self, d):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as write_file:
            json.dump(d, write_file, indent=4)

    def load(self):
        with open(self.path, "r") as read_file:
            d = json.load(read_file)
        return {int(k): v for k, v in d.items()}


def get_database_read_ids(config, forced=False):

    logger.info(f"Getting read_ids_mapping.")

    target = data_dir(config, name="database", suffix="json")

    database = DB(target)

    if do_run(target, forced=forced):
        logger.info(f"Computing read_ids_mapping.")
        read_ids_mapping = results.get_database_read_ids(config)
        database.save(read_ids_mapping)

    else:
        logger.info(f"Loading read_ids_mapping.")
        read_ids_mapping = database.load()

    return read_ids_mapping


#%%


def run_single_config(config):

    # if not main process (and haven't been initialized before)
    name = current_process().name
    if "SpawnPoolWorker" in name or "SpawnProcess" in name:
        setup_logger(
            log_port=config["log_port"],
            log_path=config["log_path"],
        )

    current_process().name = config["sample"]

    run_LCA(config)
    df_mismatches = get_df_mismatches(config)
    df_fit_results = get_df_fit_results(config, df_mismatches, forced=True)
    df_results = get_df_results(config, df_mismatches, df_fit_results)
    # read_ids_mapping = get_database_read_ids(config)

    logger.info("Finished.")

    return df_mismatches, df_fit_results, df_results
