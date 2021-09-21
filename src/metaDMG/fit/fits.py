from collections import defaultdict
import warnings
import joblib
import numpy as np
import numpyro
import pandas as pd
from logger_tt import logger
from multiprocessing import Pool
import gc
from metaDMG.fit import bayesian, frequentist, fit_utils

numpyro.enable_x64()

#%%

timeout_first_fit = 5 * 60  # 5 minutes, very first fit
timeout_subsequent_fits = 60  # 1 minute

#%%


def get_groupby(df_mismatches):
    return df_mismatches.groupby("tax_id", sort=False, observed=True)


def group_to_numpyro_data(config, group):

    forward = "CT"
    forward_ref = forward[0]
    reverse = "GA"
    reverse_ref = reverse[0]

    x = np.array(group.iloc[: config["max_position"]]["position"], dtype=int)

    k_forward = np.array(group.iloc[: config["max_position"]][forward], dtype=int)
    N_forward = np.array(group.iloc[: config["max_position"]][forward_ref], dtype=int)

    k_reverse = np.array(group.iloc[-config["max_position"] :][reverse], dtype=int)
    N_reverse = np.array(group.iloc[-config["max_position"] :][reverse_ref], dtype=int)

    data = {
        "x": np.concatenate([x, -x]),
        "k": np.concatenate([k_forward, k_reverse]),
        "N": np.concatenate([N_forward, N_reverse]),
    }

    return data


#%%


def add_count_information(config, fit_result, group, data):
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


def fit_single_group(
    config,
    group,
    mcmc_PMD=None,
    mcmc_null=None,
):

    fit_result = {}

    data = group_to_numpyro_data(config, group)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        fit_all, fit_forward, fit_reverse = frequentist.make_fits(fit_result, data)

    add_count_information(config, fit_result, group, data)

    if mcmc_PMD is not None and mcmc_null is not None:
        bayesian.make_fits(fit_result, data, mcmc_PMD, mcmc_null)

    return fit_result


def compute_fits_seriel(config, df_mismatches):

    # Do not initialise MCMC if config["bayesian"] is False
    mcmc_PMD, mcmc_null = bayesian.init_mcmcs(config)

    groupby = get_groupby(df_mismatches)

    d_fit_results = {}

    # for tax_id, group in tqdm(groupby, total=len(groupby)):
    for i, (tax_id, group) in enumerate(groupby):
        # break
        try:
            d_fit_results[tax_id] = fit_single_group(
                config,
                group,
                mcmc_PMD,
                mcmc_null,
            )
        except:
            logger.error(f"Error here: tax_id = {tax_id}")
            logger.error(f"Error here:  group = {group}")
            logger.error(f"Error here: config = {config}")

        # if config["bayesian"] and i > 0 and i % 1000 == 0:
        #     logger.debug("Reducing memory")
        #     mcmc_PMD, mcmc_null = bayesian.init_mcmcs(config)
        #     gc.collect()

    return d_fit_results


from tqdm import tqdm


def compute_fits_parallel_worker(df_mismatches_config):

    df_mismatches, config, position = df_mismatches_config

    # Do not initialise MCMC if config["bayesian"] is False
    mcmc_PMD, mcmc_null = bayesian.init_mcmcs(config)

    groupby = get_groupby(df_mismatches)

    d_fit_results = {}

    # for tax_id, group in tqdm(groupby, total=len(groupby), position=position):
    for tax_id, group in groupby:
        try:
            d_fit_results[tax_id] = fit_single_group(
                config,
                group,
                mcmc_PMD,
                mcmc_null,
            )
        except:
            logger.error(f"Error here: tax_id = {tax_id}")
            logger.error(f"Error here:  group = {group}")
            logger.error(f"Error here: config = {config}")
    return d_fit_results


def compute_fits_parallel(config, df_mismatches):

    cores = config["cores_pr_fit"]
    tax_id_list = np.array_split(df_mismatches["tax_id"].unique(), cores)

    dfs = []
    for position, tax_ids in enumerate(tax_id_list):
        dfs.append(
            (
                df_mismatches.query(f"tax_id in {list(tax_ids)}"),
                config,
                position,
            )
        )

    d_fit_results = {}
    with Pool(processes=cores) as pool:
        for d_fit_results_ in pool.imap_unordered(compute_fits_parallel_worker, dfs):
            d_fit_results.update(d_fit_results_)

    return d_fit_results


#%%


def match_tax_id_order_in_df_fit_results(df_fit_results, df_mismatches):
    tax_ids_all = pd.unique(df_mismatches.tax_id)
    ordered = [tax_id for tax_id in tax_ids_all if tax_id in df_fit_results.index]
    return df_fit_results.loc[ordered]


# def move_column_inplace(df, col, pos=0):
#     col = df.pop(col)
#     df.insert(pos, col.name, col)


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
        for tax_id_non_unique in tax_ids_non_unique:
            d_fit_results[tax_id_non_unique] = d_fit_results[tax_id_unique]


def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])


def read_stats(config):

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

    from io import StringIO

    # TODO: remove when Thorfinn updates his code
    with open(config["path_mismatches_stat"], "r") as f:
        data = f.read()

    data = data.replace("\t\t", "\t'")
    data = data.replace('1:root:"no rank"', """1:root:"no rank"'""")

    string_columns = ["tax_name", "tax_rank", "tax_path"]

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


def compute(config, df_mismatches):

    # find unique tax_ids (when compairing the mismatches matrices)
    # such that only those are fitted
    unique, duplicates = compute_duplicates(df_mismatches)

    logger.debug(
        f"Instead of fitting all {df_mismatches.tax_id.nunique()} tax IDs, "
        f"only fit the {len(unique)} unique ones."
    )

    df_mismatches_unique = df_mismatches.query(f"tax_id in {unique}")

    if config["cores_pr_fit"] == 1:
        logger.debug(f"Fitting in seriel.")
        d_fit_results = compute_fits_seriel(config, df_mismatches_unique)
    else:
        logger.debug(f"Fitting in parallel with {config['cores_pr_fit']} cores.")
        d_fit_results = compute_fits_parallel(config, df_mismatches_unique)

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

    df_fit_results = df_fit_results[cols_ordered]

    return df_fit_results
