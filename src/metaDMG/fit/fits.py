#%%
import itertools
import warnings
from collections import defaultdict
from multiprocessing import Pool

import joblib
import numpy as np
import numpyro
import pandas as pd
from logger_tt import logger

from metaDMG.fit import bayesian, fit_utils, frequentist


numpyro.enable_x64()

#%%

timeout_first_fit = 5 * 60  # 5 minutes, very first fit
timeout_subsequent_fits = 60  # 1 minute

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
        bayesian.make_fits(fit_result, data, mcmc_PMD, mcmc_null)

    return fit_result


from tqdm import tqdm


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

        d_fit_results[tax_id] = fit_single_group(
            config,
            group,
            mcmc_PMD,
            mcmc_null,
        )

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


def get_list_of_groups(config, df_mismatches, N_in_each_group=100):

    cores_per_sample = config["cores_per_sample"]

    tax_ids = df_mismatches["tax_id"].unique()

    if not config["bayesian"]:
        N_splits = cores_per_sample
    else:
        # make splits, each with N_in_each_group groups in them
        N_splits = len(tax_ids) // N_in_each_group + 1

    tax_id_list = np.array_split(tax_ids, N_splits)

    dfs = []
    for position, tax_ids in enumerate(tax_id_list):
        dfs.append(
            (
                df_mismatches.query(f"tax_id in {list(tax_ids)}"),
                config,
                use_progressbar(config, position),
            )
        )
    return dfs


def compute_fits_parallel(config, df_mismatches, N_in_each_group=100):

    cores_per_sample = config["cores_per_sample"]

    dfs = get_list_of_groups(
        config,
        df_mismatches,
        N_in_each_group=N_in_each_group,
    )

    d_fit_results = {}
    with Pool(processes=cores_per_sample) as pool:
        for d_fit_results_ in pool.imap_unordered(
            compute_fits_parallel_worker,
            dfs,
        ):
            d_fit_results.update(d_fit_results_)

    return d_fit_results


def compute_fits_parallel_Bayesian(config, df_mismatches, N_in_each_group=100):

    cores_per_sample = config["cores_per_sample"]

    dfs = get_list_of_groups(
        config=config,
        df_mismatches=df_mismatches,
        N_in_each_group=N_in_each_group,
    )

    do_progressbar = config["parallel_samples"] == 1 or len(config["samples"]) == 1

    it = grouper(dfs, cores_per_sample)
    if do_progressbar:
        it = tqdm(
            grouper(dfs, cores_per_sample),
            total=len(dfs) // cores_per_sample,
            unit="chunks",
        )

    d_fit_results = {}
    for dfs_ in it:
        # break

        if do_progressbar:
            size = dfs_[0][0]["tax_id"].nunique()
            it.set_description(f"Fitting in chunks of size {size}")

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


def read_stats_lca(config):

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


def read_stats_non_lca(config):

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


def read_stats(config):
    if config["damage_mode"] == "lca":
        return read_stats_lca(config)
    else:
        return read_stats_non_lca(config)


#%%


def compute(config, df_mismatches):

    # filter out tax_id's with 0 k_sum_total
    tax_ids_to_drop = set(df_mismatches.query("k_sum_total == 0")["tax_id"].unique())
    if len(tax_ids_to_drop) > 0:
        logger.debug(f"Dropping the following Tax IDs since k_sum_total == 0:")
        logger.debug(tax_ids_to_drop)
    df_mismatches = df_mismatches.query("k_sum_total > 0")

    # find unique tax_ids (when compairing the mismatches matrices)
    # such that only those are fitted
    unique, duplicates = compute_duplicates(df_mismatches)

    logger.debug(
        f"Instead of fitting all {df_mismatches['tax_id'].nunique()} tax IDs, "
        f"only fit the {len(unique)} unique ones."
    )

    df_mismatches_unique = df_mismatches.query(f"tax_id in {unique}")

    if config["bayesian"]:
        logger.debug(f"compute_fits_parallel_Bayesian")
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
            logger.debug(
                f"Fitting in parallel with {config['cores_per_sample']} cores."
            )
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

    df_stats = read_stats(config)

    df_fit_results = pd.merge(df_fit_results, df_stats, on="tax_id")

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
