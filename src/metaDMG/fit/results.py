#%%
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
from logger_tt import logger
from scipy.stats import betabinom as sp_betabinom


#%%


def get_number_of_lines(filename):
    with open(filename, "r") as f:
        counter = 0
        for _ in f:
            counter += 1
    return counter


def split(strng, sep, pos):
    strng = strng.split(sep)
    return sep.join(strng[:pos]), sep.join(strng[pos:])


def extract_tax_id_and_read_id(row):
    read_id_plus_info, tax_path = split(row, sep="\t", pos=1)
    tax_id = int(tax_path.split(":")[0])
    read_id, _ = split(read_id_plus_info, sep=":", pos=-4)
    return tax_id, read_id


def read_filename_lca(file_lca):

    N_lines = get_number_of_lines(file_lca)

    d_tax_id_to_read_ids = defaultdict(set)
    with open(file_lca, "r") as f:

        for irow, row in enumerate(f):

            if irow == 0:
                continue

            tax_id, read_id = extract_tax_id_and_read_id(row)
            d_tax_id_to_read_ids[tax_id].add(read_id)

    d_tax_id_to_read_ids = dict(d_tax_id_to_read_ids)

    for key, val in d_tax_id_to_read_ids.items():
        d_tax_id_to_read_ids[key] = list(val)

    return d_tax_id_to_read_ids


def compute_df_mismatches_wide(df_mismatches):

    # fix old df_mismatches using |z| instead of |x|
    if "|z|" in df_mismatches.columns:
        df_mismatches = df_mismatches.rename(columns={"|z|": "|x|"})
        logger.info(
            "df_mismatches uses the old notation, '|z|', instead of '|x|'. "
            "Consider deleting the old mismatch file and run again."
        )

    max_pos = df_mismatches.position.max()

    d_direction = {
        "forward": {
            "query": "position > 0",
            "symbol": "+",
        },
        "reverse": {
            "query": "position < 0",
            "symbol": "-",
        },
    }

    df_mismatches_wide = []
    for direction in ["forward", "reverse"]:
        for variable in ["k", "N", "f"]:
            col_names = [
                f"{variable}{d_direction[direction]['symbol']}{i}"
                for i in range(1, max_pos + 1)
            ]
            columns = {i + 1: col for i, col in enumerate(col_names)}

            df_mismatches_wide.append(
                df_mismatches.query(d_direction[direction]["query"])
                .pivot(index="tax_id", columns="|x|", values=variable)
                .rename(columns=columns)
            )

    df_mismatches_wide = pd.concat(df_mismatches_wide, axis="columns")

    return df_mismatches_wide


def merge(
    config,
    df_mismatches,
    df_fit_results,
):

    # merge the mismatches counts (as a wide dataframe) into the fit results dataframe
    df_mismatches_wide = compute_df_mismatches_wide(df_mismatches)
    df_results = pd.merge(df_fit_results, df_mismatches_wide, on=["tax_id"])

    columns_order = [
        "tax_id",
        "tax_name",
        "tax_rank",
        "sample",
        "N_reads",
        "N_alignments",
        #
        "lambda_LR",
        "D_max",
        "mean_L",
        "mean_GC",
        "q",
        "A",
        "c",
        "phi",
        "rho_Ac",
        "valid",
        "asymmetry",
    ]

    # if local or global damage
    if config["damage_mode"] in ("local", "global"):
        for col in ["tax_name", "tax_rank", "N_alignments"]:
            columns_order.remove(col)

    columns_order += [col for col in df_fit_results.columns if not col in columns_order]
    columns_order += list(df_mismatches_wide.columns)

    df_results = df_results[columns_order]

    return df_results


def get_database_read_ids(config):
    file_lca = config["path_lca"]
    read_ids_mapping = read_filename_lca(file_lca)
    return read_ids_mapping

    # db = database(filename_database)
    # db.save(d_tax_id_to_read_ids)


#%%
