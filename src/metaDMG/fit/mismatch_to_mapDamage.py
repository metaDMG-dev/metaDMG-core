#%%

import numpy as np
import pandas as pd

from metaDMG import __version__ as version
from metaDMG.fit import mismatches


#%%


def make_reverse_group(group):
    group_reverse = pd.DataFrame(0, index=group.index, columns=group.columns)
    group_reverse.loc[:, "tax_id"] = group.loc[:, "tax_id"]
    group_reverse.loc[:, "direction"] = "3'"
    group_reverse.loc[:, "position"] = -group.loc[:, "position"]
    group_reverse.loc[:, "|x|"] = group.loc[:, "|x|"]
    group_reverse.loc[:, "sample"] = group.loc[:, "sample"]
    return group_reverse


def append_reverse_groups(df_mismatch):
    groups = []
    for i, group in df_mismatch.groupby(["tax_id"], sort=False):
        group_reverse = make_reverse_group(group)
        group_combined = pd.concat([group, group_reverse])
        groups.append(group_combined)
    df_mismatch = pd.concat(groups)
    return df_mismatch


def df_mismatch_to_mapDamage(df_mismatch):

    df_mapDamage = df_mismatch.copy()

    # if forward only, fill in zeros for reverse direction
    if "3'" not in df_mapDamage["direction"].unique():
        df_mapDamage = append_reverse_groups(df_mapDamage)

    bases = ["A", "C", "G", "T"]
    for base in bases:
        if base not in df_mapDamage.columns:
            mismatches.add_reference_count(df_mapDamage, ref=base)

    df_mapDamage["Total"] = df_mapDamage[bases].sum(axis=1)

    # fmt: off
    columns = [
        "Chr", "End", "Std", "Pos",
        "A", "C", "G", "T", "Total",
        "G>A", "C>T", "A>G", "T>C", "A>C", "A>T", "C>G", "C>A", "T>G", "T>A", "G>C", "G>T",
        "A>-", "T>-", "C>-", "G>-",
        "->A", "->T", "->C", "->G",
        "S",
    ]
    # fmt: on

    d_rename = {
        "tax_id": "Chr",
        "position": "Pos",
    }

    idx_start = columns.index("G>A")
    idx_end = columns.index("G>T") + 1
    for sub in columns[idx_start:idx_end]:
        d_rename[sub[0] + sub[-1]] = sub

    df_mapDamage = df_mapDamage.rename(columns=d_rename)
    df_mapDamage["End"] = np.where(df_mapDamage["Pos"] > 0, "5p", "3p")
    df_mapDamage["Std"] = "+"
    df_mapDamage["Pos"] = np.abs(df_mapDamage["Pos"])

    for col in columns[idx_end:]:
        df_mapDamage[col] = 0

    df_mapDamage = df_mapDamage.loc[:, columns]

    return df_mapDamage


def convert(filename, csv_out):

    df_mismatch = pd.read_parquet(filename)
    df_mapDamage = df_mismatch_to_mapDamage(df_mismatch)

    out = ""
    out += (
        f"# table produced by metaDMG version {version} \n"
        f"# using mismatch file {filename.name} \n"
        f"# Chr: Tax ID, "
        f"End: from which termini of DNA sequences, "
        f"Std: Defined to be relative to + strand \n"
    )

    out += df_mapDamage.to_csv(index=False, sep="\t")

    with open(csv_out, "w", encoding="utf-8") as file:
        file.write(out)
