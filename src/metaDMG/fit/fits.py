#%%
import itertools
import warnings
from collections import defaultdict
from math import ceil
from multiprocessing import Pool

import joblib
import numpy as np
import numpyro
import pandas as pd
from logger_tt import logger
from tqdm import tqdm

from metaDMG.errors import BadDataError, FittingError
from metaDMG.fit import bayesian, fit_utils, frequentist
from metaDMG.utils import Config


numpyro.enable_x64()

#%%

BAYESIAN_MAXIMUM_SIZE = 100

#%%


def get_groupby(df_mismatches):
    return df_mismatches.groupby("tax_id", sort=False, observed=True)


def group_to_numpyro_data(config, group):

    x = np.array(group.iloc[: config["max_position"]]["position"], dtype=int)

    if config["forward_only"]:

        forward = "CT"
        forward_ref = forward[0]

        k = np.array(group.iloc[: config["max_position"]][forward], dtype=int)
        N = np.array(group.iloc[: config["max_position"]][forward_ref], dtype=int)

        data = {"x": x, "k": k, "N": N}
        return data

    else:

        forward = "CT"
        forward_ref = forward[0]
        reverse = "GA"
        reverse_ref = reverse[0]

        k_forward = np.array(group.iloc[: config["max_position"]][forward], dtype=int)
        N_forward = np.array(
            group.iloc[: config["max_position"]][forward_ref], dtype=int
        )

        k_reverse = np.array(group.iloc[-config["max_position"] :][reverse], dtype=int)
        N_reverse = np.array(
            group.iloc[-config["max_position"] :][reverse_ref], dtype=int
        )

        data = {
            "x": np.concatenate([x, -x]),
            "k": np.concatenate([k_forward, k_reverse]),
            "N": np.concatenate([N_forward, N_reverse]),
        }

        return data


#%%


def add_count_information(fit_result, config, group, data):

    if config["forward_only"]:
        fit_result["N_x=1_forward"] = data["N"][0]
        # fit_result["N_x=1_reverse"] = np.nan

        fit_result["N_sum_total"] = data["N"].sum()
        fit_result["N_sum_forward"] = fit_result["N_sum_total"]
        # fit_result["N_sum_reverse"] = np.nan

        fit_result["N_min"] = data["N"].min()

        fit_result["k_sum_total"] = data["k"].sum()
        fit_result["k_sum_forward"] = fit_result["k_sum_total"]
        # fit_result["k_sum_reverse"] = np.nan

    else:

        fit_result["N_x=1_forward"] = data["N"][0]
        fit_result["N_x=1_reverse"] = data["N"][config["max_position"]]

        fit_result["N_sum_total"] = data["N"].sum()
        fit_result["N_sum_forward"] = data["N"][: config["max_position"]].sum()
        fit_result["N_sum_reverse"] = data["N"][config["max_position"] :].sum()

        fit_result["N_min"] = data["N"].min()

        fit_result["k_sum_total"] = data["k"].sum()
        fit_result["k_sum_forward"] = data["k"][: config["max_position"]].sum()
        fit_result["k_sum_reverse"] = data["k"][config["max_position"] :].sum()


#%%


# def timer_fit_MAP(config, data):
#     # data = group_to_numpyro_data(config, group)
#     # %timeit timer_fit_MAP(config, data)
#     fit_result = {}
#     with warnings.catch_warnings():
#         warnings.filterwarnings("ignore")
#         fit_all, fit_forward, fit_reverse = frequentist.make_fits(fit_result, data)


# def timer_fit_bayesian(config, data, mcmc_PMD, mcmc_null):
#     # data = group_to_numpyro_data(config, group)
#     # %timeit timer_fit_bayesian(config, data, mcmc_PMD, mcmc_null)
#     fit_result = {}
#     bayesian.make_fits(fit_result, data, mcmc_PMD, mcmc_null)


#%%


def fit_single_group(
    config,
    group,
    mcmc_PMD=None,
    mcmc_null=None,
):

    fit_result = {}

    data = group_to_numpyro_data(config, group)
    sample = config["sample"]
    tax_id = group["tax_id"].iloc[0]

    if data["N"].sum() == 0:
        from metaDMG.fit.serial import _setup_logger

        _setup_logger(config)

        s = f"No data for tax_id {tax_id}, sample = {sample}, i.e. sum(N) = 0. "
        s += "Skipping the fit."
        logger.warning(s)
        return None

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")

        frequentist.make_fits(
            config,
            fit_result,
            data,
            sample,
            tax_id,
        )  # fit_all, fit_forward, fit_reverse

    add_count_information(fit_result, config, group, data)

    if mcmc_PMD is not None and mcmc_null is not None:
        try:
            bayesian.make_fits(fit_result, data, mcmc_PMD, mcmc_null)
        except:
            from metaDMG.fit.serial import _setup_logger

            _setup_logger(config)
            s = f"Error in bayesian.make_fits for tax_id {tax_id}, sample = {sample}."
            s += "Skipping the Bayesian fit."
            logger.warning(s)

    return fit_result


def compute_fits_seriel(config, df_mismatches, with_progressbar=False):

    # Do not initialise MCMC if config["bayesian"] is False
    mcmc_PMD, mcmc_null = bayesian.init_mcmcs(config)

    groupby = get_groupby(df_mismatches)

    if with_progressbar:
        groupby = tqdm(groupby, total=len(groupby))

    d_fit_results = {}
    for tax_id, group in groupby:
        # break

        if with_progressbar:
            groupby.set_description(f"Fitting Tax ID {tax_id}")

        res = fit_single_group(
            config,
            group,
            mcmc_PMD,
            mcmc_null,
        )

        if res is not None:
            d_fit_results[tax_id] = res

    return d_fit_results


def compute_fits_parallel_worker(df_mismatches_config):
    df_mismatches, config, with_progressbar = df_mismatches_config
    return compute_fits_seriel(
        config=config,
        df_mismatches=df_mismatches,
        with_progressbar=with_progressbar,
    )


def grouper(iterable, n):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def use_progressbar(config, position):
    if config["bayesian"]:
        return False

    if config["parallel_samples"] == 1 or len(config["samples"]) == 1:
        if position == 0:
            return True

    return False


def get_list_of_groups(
    config,
    df_mismatches_unique,
    N_splits=None,
    N_maximum_group_size=BAYESIAN_MAXIMUM_SIZE,
):

    tax_ids = df_mismatches_unique["tax_id"].unique()

    if N_splits is None:
        cores_per_sample = config["cores_per_sample"]
        N_splits = cores_per_sample * ceil(
            len(tax_ids) / cores_per_sample / N_maximum_group_size
        )

    tax_id_list = np.array_split(tax_ids, N_splits)

    dfs = []
    for position, tax_ids in enumerate(tax_id_list):
        dfs.append(
            (
                df_mismatches_unique.query(f"tax_id in {list(tax_ids)}"),
                config,
                use_progressbar(config, position),
            )
        )
    return dfs


def compute_fits_parallel(
    config,
    df_mismatches_unique,
):

    cores_per_sample = config["cores_per_sample"]

    dfs = get_list_of_groups(
        config,
        df_mismatches_unique,
        N_splits=cores_per_sample,
    )

    d_fit_results = {}
    with Pool(processes=cores_per_sample) as pool:
        for d_fit_results_ in pool.imap_unordered(
            compute_fits_parallel_worker,
            dfs,
        ):
            d_fit_results.update(d_fit_results_)

    return d_fit_results


def compute_fits_parallel_Bayesian(
    config,
    df_mismatches_unique,
    N_maximum_group_size=BAYESIAN_MAXIMUM_SIZE,
):

    cores_per_sample = config["cores_per_sample"]

    dfs = get_list_of_groups(
        config=config,
        df_mismatches_unique=df_mismatches_unique,
        N_maximum_group_size=N_maximum_group_size,
    )

    do_progressbar = config["parallel_samples"] == 1 or len(config["samples"]) == 1

    if len(dfs) == 1:
        logger.debug(f"Computing Bayesian fits in serial (using 1 core).")
        d_fit_results = compute_fits_seriel(
            config,
            df_mismatches_unique,
            with_progressbar=do_progressbar,
        )
        return d_fit_results

    logger.debug(f"Computing Bayesian fits")

    d_fit_results = {}

    N_chunks = int(np.ceil(len(dfs) / cores_per_sample))

    if N_chunks == 1:

        if do_progressbar:
            dfs[0] = (dfs[0][0], dfs[0][1], True)

        with Pool(processes=cores_per_sample) as pool:
            for d_fit_results_ in pool.imap_unordered(
                compute_fits_parallel_worker,
                dfs,
            ):
                d_fit_results.update(d_fit_results_)
        return d_fit_results

    it = grouper(dfs, cores_per_sample)
    if do_progressbar:
        it = tqdm(it, total=N_chunks, unit="chunks")

    for dfs_ in it:
        # break

        if do_progressbar:
            size = dfs_[0][0]["tax_id"].nunique()
            s = f"Fitting in {N_chunks} chunks, each of size {size}, using {cores_per_sample} core(s)"
            it.set_description(s)

        with Pool(processes=cores_per_sample) as pool:
            for d_fit_results_ in pool.imap_unordered(
                compute_fits_parallel_worker,
                dfs_,
            ):
                d_fit_results.update(d_fit_results_)

    return d_fit_results


#%%


def match_tax_id_order_in_df_fit_results(df_fit_results, df_mismatches):
    tax_ids_all = pd.unique(df_mismatches["tax_id"])
    ordered = [tax_id for tax_id in tax_ids_all if tax_id in df_fit_results.index]
    return df_fit_results.loc[ordered]


def make_df_fit_results_from_fit_results(config, d_fit_results, df_mismatches):
    df_fit_results = pd.DataFrame.from_dict(d_fit_results, orient="index")
    df_fit_results["tax_id"] = df_fit_results.index
    # move_column_inplace(df_fit_results, "tax_id", pos=0)

    df_fit_results = match_tax_id_order_in_df_fit_results(df_fit_results, df_mismatches)
    df_fit_results["sample"] = config["sample"]
    categories = []
    df_fit_results = fit_utils.downcast_dataframe(
        df_fit_results, categories, fully_automatic=False
    )

    df_fit_results = df_fit_results.reset_index(drop=True)

    return df_fit_results


#%%


def compute_duplicates(df_mismatches):

    groupby = get_groupby(df_mismatches)

    duplicate_entries = defaultdict(list)
    for group in groupby:
        key = joblib.hash(group[1][fit_utils.ref_obs_bases].values)
        duplicate_entries[key].append(group[0])
    duplicate_entries = dict(duplicate_entries)

    unique = [tax_ids[0] for tax_ids in duplicate_entries.values()]
    duplicates = {tax_ids[0]: tax_ids[1:] for tax_ids in duplicate_entries.values()}

    return unique, duplicates


def de_duplicate_fit_results(d_fit_results, duplicates):

    for tax_id_unique, tax_ids_non_unique in duplicates.items():

        if not tax_id_unique in d_fit_results:
            logger.warning(f"Could not de-duplicate tax ID {tax_id_unique}.")
            continue

        for tax_id_non_unique in tax_ids_non_unique:
            d_fit_results[tax_id_non_unique] = d_fit_results[tax_id_unique]


def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])


#%%


def read_stats_lca(config: Config):

    import gzip
    from io import StringIO

    columns = [
        "tax_id",
        "tax_name",
        "tax_rank",
        "N_alignments",
        "N_reads",
        "mean_L",
        "var_L",
        "mean_GC",
        "var_GC",
        "tax_path",
    ]

    # TODO: remove when Thorfinn updates his code
    with gzip.open(config["path_mismatches_stat"], "rt") as f:
        data = f.read()

    data = data.replace("'", "")  # remove '
    data = data.replace("\t\t", "\t'")
    data = data.replace('1:root:"no rank"', """1:root:"no rank"'""")

    string_columns = ["tax_id", "tax_name", "tax_rank", "tax_path"]

    df_stats = pd.read_csv(
        StringIO(data),  # config["path_mismatches_stat"]
        sep="\t",
        skiprows=1,
        index_col=False,
        quotechar="'",
        names=columns,
        dtype={column: "string" for column in string_columns},
    )

    for column in ("tax_name", "tax_rank"):
        df_stats[column] = df_stats[column].str.replace('"', "")

    df_stats["std_L"] = np.sqrt(df_stats["var_L"])
    df_stats["std_GC"] = np.sqrt(df_stats["var_GC"])
    return df_stats


def read_stats_non_lca(config: Config):

    columns = ["tax_id", "N_reads", "mean_L", "var_L", "mean_GC", "var_GC"]

    df_stats = pd.read_csv(
        config["path_mismatches_stat"],
        sep="\t",
        names=columns,
        usecols=columns,
    )

    df_stats["std_L"] = np.sqrt(df_stats["var_L"])
    df_stats["std_GC"] = np.sqrt(df_stats["var_GC"])
    return df_stats


def read_stats(config: Config):
    if config["damage_mode"] == "lca":
        return read_stats_lca(config)
    else:
        return read_stats_non_lca(config)


def cut_minimum_reads(
    config: Config,
    df_stats: pd.DataFrame,
) -> pd.DataFrame:
    return df_stats.query(f"(N_reads >= {config['min_reads']})")


def filter_tax_ids(
    config: Config,
    df_stats: pd.DataFrame,
    df_stat_cut: pd.DataFrame,
    df_mismatches: pd.DataFrame,
) -> pd.DataFrame:
    all_tax_ids = set(df_stats["tax_id"].unique())
    good_tax_ids = set(df_stat_cut["tax_id"].unique())
    bad_tax_ids = all_tax_ids.difference(good_tax_ids)
    if len(bad_tax_ids) > 0:
        logger.debug(f"Dropping the following Tax IDs due to too few reads:")
        logger.debug(bad_tax_ids)
        logger.debug(f"with a minimum reads threshold of {config['min_reads']}.")
    return df_mismatches.query("tax_id in @good_tax_ids")


def filter_k_sum(
    config: Config,
    df_mismatches: pd.DataFrame,
) -> pd.DataFrame:

    # filter out tax_id's with 0 k_sum_total
    tax_ids_to_drop = set(df_mismatches.query("k_sum_total == 0")["tax_id"].unique())
    if len(tax_ids_to_drop) > 0:
        logger.debug(f"Dropping the following Tax IDs since k_sum_total == 0:")
        logger.debug(tax_ids_to_drop)
    return df_mismatches.query("k_sum_total > 0")


#%%


def compute(config, df_mismatches):

    df_stats = read_stats(config)
    df_stat_cut = cut_minimum_reads(config, df_stats)

    # filter out tax_id's with too few reads
    df_mismatches = filter_tax_ids(config, df_stats, df_stat_cut, df_mismatches)

    if len(df_mismatches) == 0:
        s = f"{config['sample']} cut on min reads > {config['min_reads']} made data empty."
        logger.debug("WARNING: BadDataError")
        logger.debug(s)
        raise BadDataError(s)

    # # filter out tax_id's with 0 k_sum_total
    # df_mismatches = filter_k_sum(config, df_mismatches)

    # if len(df_mismatches) == 0:
    #     s = f"{config['sample']} df_mismatches.query('k_sum_total > 0') is empty."
    #     logger.debug("WARNING: BadDataError")
    #     logger.debug(s)
    #     raise BadDataError(s)

    # find unique tax_ids (when compairing the mismatches matrices)
    # such that only those are fitted
    unique, duplicates = compute_duplicates(df_mismatches)

    logger.debug(
        f"Instead of fitting all {df_mismatches['tax_id'].nunique()} tax IDs, "
        f"only fit the {len(unique)} unique ones."
    )

    df_mismatches_unique = df_mismatches.query(f"tax_id in {unique}")

    if config["bayesian"]:
        # logger.debug(f"Computing Bayesian fits")
        d_fit_results = compute_fits_parallel_Bayesian(config, df_mismatches_unique)

    else:
        if config["cores_per_sample"] == 1:
            logger.debug(f"Fitting in seriel.")

            if config["parallel_samples"] == 1 or len(config["samples"]) == 1:
                with_progressbar = True
            else:
                with_progressbar = False

            d_fit_results = compute_fits_seriel(
                config,
                df_mismatches_unique,
                with_progressbar=with_progressbar,
            )

        else:
            s = f"Fitting in parallel with {config['cores_per_sample']} cores."
            logger.debug(s)
            d_fit_results = compute_fits_parallel(
                config,
                df_mismatches_unique,
            )

    de_duplicate_fit_results(d_fit_results, duplicates)

    df_fit_results = make_df_fit_results_from_fit_results(
        config,
        d_fit_results,
        df_mismatches,
    )

    df_fit_results = pd.merge(df_fit_results, df_stat_cut, on="tax_id")

    cols_ordered = [
        "tax_id",
        "tax_name",
        "tax_rank",
        "N_reads",
        "N_alignments",
        "lambda_LR",
        "D_max",
        "mean_L",
        "std_L",
        "mean_GC",
        "std_GC",
        "tax_path",
        *df_fit_results.loc[:, "D_max_std":"sample"].columns.drop("tax_id"),
    ]

    # if local or global damage
    if config["damage_mode"] in ("local", "global"):
        for col in ["tax_name", "tax_rank", "N_alignments", "tax_path"]:
            cols_ordered.remove(col)

    df_fit_results = df_fit_results[cols_ordered]

    return df_fit_results


# %%
#
