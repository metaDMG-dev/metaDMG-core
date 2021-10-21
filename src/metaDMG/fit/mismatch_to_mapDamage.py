import numpy as np
import pandas as pd

from metaDMG.fit import mismatches
from metaDMG import __version__ as version


def df_mismatch_to_mapDamage(df_mismatch):

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

    df_mapDamage = df_mismatch.copy()

    mismatches.add_reference_counts(df_mapDamage, ref="A")
    mismatches.add_reference_counts(df_mapDamage, ref="T")
    df_mapDamage["Total"] = df_mapDamage[["A", "C", "G", "T"]].sum(axis=1)

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
