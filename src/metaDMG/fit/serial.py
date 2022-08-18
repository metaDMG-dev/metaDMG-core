#%%
import shlex
import shutil
import subprocess

# import json
from collections import Counter
from multiprocessing import current_process
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
from logger_tt import logger

from metaDMG import utils
from metaDMG.errors import (
    AlignmentFileError,
    BadDataError,
    Error,
    MismatchFileError,
    metadamageError,
)
from metaDMG.fit import fits, mismatches, results
from metaDMG.loggers.loggers import setup_logger
from metaDMG.utils import Config


#%%


def do_run(targets, force=False):

    if force:
        logger.info("Using force load, beware.")

    if force:
        return True

    if not isinstance(targets, list):
        targets = [targets]

    if all(Path(target).exists() for target in targets):
        return False
    else:
        return True


def do_load(targets, force=False):
    return not do_run(targets, force=force)


def data_dir(config: Config, name, suffix="parquet"):
    target = config["output_dir"] / name / f"{config['sample']}.{name}.{suffix}"
    return target


#%%


def _exists_in_config(s: str, key: str, config: Config) -> str:
    return f"-{s} {config[key]}" if key in config else ""


def get_LCA_command(config: Config) -> str:
    outnames = config["path_tmp"] / config["sample"]
    lca_rank = f"-lca_rank {config['lca_rank']}" if config["lca_rank"] != "" else ""
    simscorelow = _exists_in_config("simscorelow", "min_similarity_score", config)
    simscorehigh = _exists_in_config("simscorehigh", "max_similarity_score", config)
    editdistmin = _exists_in_config("editdistmin", "min_edit_dist", config)
    editdistmax = _exists_in_config("editdistmax", "max_edit_dist", config)

    command = (
        f"{config['metaDMG_cpp']} lca "
        f"-bam {config['bam']} "
        f"-outnames {outnames} "
        f"-names {config['names']} "
        f"-nodes {config['nodes']} "
        f"-acc2tax {config['acc2tax']} "
        f"{simscorelow} "
        f"{simscorehigh} "
        f"{editdistmin} "
        f"{editdistmax} "
        f"{lca_rank} "
        f"-minmapq {config['min_mapping_quality']} "
        f"-howmany {config['max_position']} "
        f"-weighttype {config['weight_type']} "
        f"-fix_ncbi {config['custom_database']} "
        f"-tempfolder {config['path_tmp']}/ "
    )
    return command[:-1]


def get_LCA_mismatches_command(config: Config) -> str:
    sample = config["sample"]
    bdamage = config["path_tmp"] / f"{sample}.bdamage.gz"
    lca_stat = config["path_tmp"] / f"{sample}.stat"

    command = (
        f"{config['metaDMG_cpp']} print_ugly "
        f"{bdamage} "
        f"-names {config['names']} "
        f"-nodes {config['nodes']} "
        f"-lcastat {lca_stat} "
    )
    return command[:-1]


#%%


def get_runmode(config: Config) -> int:

    runmode = config["damage_mode"]

    if runmode == "lca":
        raise AssertionError(f"mixing getdamage and lca")

    # damage patterns will be calculated for each chr/scaffold contig.
    elif runmode == "local":
        return 1

    # one global estimate
    elif runmode == "global":
        return 0

    raise AssertionError(f"Got wrong runmode. Got: {runmode}")


def get_damage_command(config: Config) -> str:
    "'Direct' damage, no LCA"

    outname = config["path_tmp"] / config["sample"]
    runmode = get_runmode(config)

    command = (
        f"{config['metaDMG_cpp']} getdamage "
        f"--minlength 10 "
        f"--printlength {config['max_position']} "
        f"--threads 8 "
        f"--runmode {runmode} "
        f"--outname {outname} "
        f"{config['bam']} "
    )
    return command[:-1]


def get_damage_ugly_command(config: Config) -> str:
    bdamage = config["path_tmp"] / f"{config['sample']}.bdamage.gz"
    command = f"{config['metaDMG_cpp']} print_ugly {bdamage} -bam {config['bam']}"
    return command


#%%


def move_files(config: Config) -> None:

    sample = config["sample"]
    path_tmp = config["path_tmp"]

    mismatch = path_tmp / f"{sample}.bdamage.gz.uglyprint.mismatch.txt.gz"
    stat = path_tmp / f"{sample}.bdamage.gz.uglyprint.stat.txt.gz"

    d_move_source_target = {
        mismatch: config["path_mismatches_txt"],
        stat: config["path_mismatches_stat"],
        path_tmp / f"{sample}.lca.gz": config["path_lca"],
        path_tmp / f"{sample}.log": config["path_lca_log"],
    }
    for source_path, target_path in d_move_source_target.items():
        logger.debug(f"Moving {source_path} to {target_path}.")
        if not source_path.is_file():
            raise metadamageError(
                f"'{source_path}' does not exist. \nIf you use a custom database, "
                "remember to use the bool flag --custom-database when creating "
                "the config file."
            )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source_path, target_path)


def move_files_non_lca(config: Config) -> None:

    sample = config["sample"]
    path_tmp = config["path_tmp"]

    mismatch = path_tmp / f"{sample}.bdamage.gz.uglyprint.mismatch.txt.gz"
    stat = path_tmp / f"{sample}.stat"

    d_move_source_target = {
        mismatch: config["path_mismatches_txt"],
        stat: config["path_mismatches_stat"],
    }
    for source_path, target_path in d_move_source_target.items():
        logger.debug(f"Moving {source_path} to {target_path}.")
        if not source_path.is_file():
            raise metadamageError(f"{source_path} does not exist.")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(source_path, target_path)


#%%


def create_tmp_dir(config: Config) -> None:
    config["path_tmp"].mkdir(parents=True, exist_ok=True)


def delete_tmp_dir(config: Config) -> None:
    utils.remove_directory(config["path_tmp"])


#%%


def run_command(command: str):

    p = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    for line in iter(p.stdout.readline, b""):  # type: ignore
        if line:
            line = line.decode("utf-8")
            if line.endswith("\n"):
                line = line[:-1]
            yield line

    # waits for the process to finish and returns the returncode
    yield p.wait()


def handle_returncode(command, line, counter):

    returncode = line
    if returncode != 0:
        s = f"{command} did not terminate properly. See log file for more information."
        raise metadamageError(s)

    lines_hidden = {key: val for key, val in counter.items() if val >= 3}
    if len(lines_hidden) > 0:
        logger.debug(f"Hid the following lines: {lines_hidden}.")
    logger.debug(f"Got return code {returncode} from {command}.")


def run_command_helper(config: Config, command: str):

    # add a counter to avoid too many similar lines
    counter = Counter()
    for line in run_command(command):

        # if finished, check returncode
        if isinstance(line, int):
            return handle_returncode(command, line, counter)

        if "ERROR: We require files to be sorted by readname, will exit" in line:
            logger.debug(line)
            s = f"The alignment file ({config['bam']}) has to be sorted by filename. "
            raise metadamageError(s)

        # continue running and logging
        if counter[line] < 3:
            logger.debug(line)

        # do not print the same line more than 3 times
        elif counter[line] == 3:
            # -> Problem finding level for rank: serotype
            logger.debug("	...")
            logger.debug("	...")
            logger.debug("	...")

        counter[line] += 1


#%%


def run_LCA(config: Config, force: bool = False) -> None:

    logger.info(f"Getting LCA.")

    targets = [
        config["path_mismatches_txt"],
        config["path_mismatches_stat"],
        config["path_lca"],
    ]

    if do_run(targets, force=force):

        if not BAM_file_is_valid(config):
            raise AlignmentFileError(
                f"{config['sample']}: The alignment file is invalid."
            )

        logger.info(f"LCA has to be computed. This can take a while, please wait.")

        command_LCA = get_LCA_command(config)
        command_LCA_mismatches = get_LCA_mismatches_command(config)

        create_tmp_dir(config)

        logger.debug(command_LCA)
        run_command_helper(config, command_LCA)

        logger.debug(command_LCA_mismatches)
        run_command_helper(config, command_LCA_mismatches)

        move_files(config)
        delete_tmp_dir(config)

    else:
        logger.info(f"LCA already been run before.")


#%%


def run_damage_no_lca(config: Config, force: bool = False) -> None:

    logger.info(f"Getting damage.")

    targets = [
        config["path_mismatches_txt"],
        config["path_mismatches_stat"],
    ]

    if do_run(targets, force=force):

        if not BAM_file_is_valid(config):
            raise AlignmentFileError(
                f"{config['sample']}: The alignment file is invalid."
            )

        logger.info(f"Computing damage. NOTE: NO LCA.")

        command_damage = get_damage_command(config)
        command_damage_ugly = get_damage_ugly_command(config)

        create_tmp_dir(config)

        logger.debug(command_damage)
        run_command_helper(config, command_damage)

        logger.debug(command_damage_ugly)
        run_command_helper(config, command_damage_ugly)

        move_files_non_lca(config)
        delete_tmp_dir(config)

    else:
        logger.info(f"Damage has already been computed before. NOTE: NO LCA.")


#%%


def run_cpp(config: Config, force: bool = False) -> None:
    if config["damage_mode"] == "lca":
        run_LCA(config, force=force)
    else:
        run_damage_no_lca(config, force=force)


#%%


def get_df_mismatches(config: Config, force: bool = False) -> pd.DataFrame:

    logger.info(f"Getting df_mismatches")

    target = data_dir(config, name="mismatches")

    if do_run(target, force=force):
        logger.info(f"Computing df_mismatches.")
        df_mismatches = mismatches.compute(config)
        target.parent.mkdir(parents=True, exist_ok=True)
        df_mismatches.to_parquet(target)

    else:
        logger.info(f"Loading df_mismatches.")
        df_mismatches = pd.read_parquet(target)

    return df_mismatches


#%%


def dataframe_columns_contains(df: pd.DataFrame, s: str) -> bool:
    return any(s in column for column in df.columns)


def get_df_fit_results(
    config: Config,
    df_mismatches: pd.DataFrame,
    force: bool = False,
) -> pd.DataFrame:

    logger.info(f"Getting df_fit_results.")

    target = data_dir(config, name="fit_results")
    if do_load(target, force=force):
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
    target.parent.mkdir(parents=True, exist_ok=True)
    df_fit_results.to_parquet(target)

    return df_fit_results


#%%


def get_df_results(
    config: Config,
    df_mismatches: pd.DataFrame,
    df_fit_results: pd.DataFrame,
    force: bool = False,
) -> pd.DataFrame:

    logger.info(f"Getting df_results.")

    target = data_dir(config, name="results")

    if do_load(target, force=force):
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
    df_results = results.merge(config, df_mismatches, df_fit_results)
    target.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_parquet(target)

    return df_results


#%%


def _setup_logger(config: Config) -> None:
    # if not main process (and haven't been initialized before)
    name = current_process().name
    if "SpawnPoolWorker" in name or "SpawnProcess" in name:
        setup_logger(
            log_port=config["log_port"],
            log_path=config["log_path"],
        )
    current_process().name = config["sample"]


def BAM_file_is_valid(config: Config) -> bool:

    if not config["bam"].is_file():
        logger.error(f"The sample bam file does not exist: {config['bam']}.")
        return False

    if config["bam"].stat().st_size == 0:
        logger.error(f"The sample bam file is of size 0: {config['bam']}.")
        return False

    return True


#%%


def run_single_config(
    config: Config,
) -> Optional[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:

    _setup_logger(config)

    force = config["force"]

    try:
        run_cpp(config, force=force)
    except metadamageError as e:
        logger.exception(
            f"{config['sample']} | "
            f"metadamageError with run_LCA. See log-file for more information."
        )
        raise e
    except AlignmentFileError as e:
        logger.exception(
            f"{config['sample']} | "
            f"Bad alignment file. See log-file for more information."
        )
        raise e
    except KeyboardInterrupt:
        logger.info("Got KeyboardInterrupt. Cleaning up.")
        delete_tmp_dir(config)
        raise KeyboardInterrupt

    try:
        df_mismatches = get_df_mismatches(config, force=force)
    except MismatchFileError as e:
        logger.exception(
            f"{config['sample']} | "
            f"MismatchFileError with get_df_mismatches. "
            f"See log-file for more information."
        )
        raise e

    try:
        df_fit_results = get_df_fit_results(config, df_mismatches, force=force)
    except BadDataError as e:
        logger.warning(
            f"{config['sample']} | "
            f"BadDataError happened while fitting, see log file for more info. "
            f"Skipping for now."
        )
        raise e

    df_results = get_df_results(config, df_mismatches, df_fit_results, force=force)
    # read_ids_mapping = get_database_read_ids(config)

    logger.info("Finished.")
    return df_mismatches, df_fit_results, df_results


def run_single_config_count_errors(
    config: Config,
) -> int:
    """Allows for using pool.map() (multiprocessing) while also counting the errors.

    Parameters
    ----------
    config
        A config file.

    Returns
    -------
        0 if no error, 1 if error
    """

    try:
        run_single_config(config)
        return 0
    except:
        return 1
