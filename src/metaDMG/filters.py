from pathlib import Path
from typing import Optional

import pandas as pd

from metaDMG.utils import append_fit_predictions, get_results_dir


def load_results(
    config_file: Optional[Path] = None,
    results_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Load the results from either a config file or a results-directory

    Parameters
    ----------
    config_file
        The the config file to use to locate the results directory, by default None
    results_dir
        The results directory, by default None

    Returns
    -------
        A dataframe of all the results
    """
    results_dir = get_results_dir(
        config_file=config_file,
        results_dir=results_dir,
    )
    df_results = pd.read_parquet(results_dir)
    return df_results


def filter_results(
    df_results: pd.DataFrame,
    query: str,
) -> pd.DataFrame:
    """Filter the results given a Pandas query

    Parameters
    ----------
    df_results
        Input dataframe
    query
        Pandas query

    Returns
    -------
        Output dataframe
    """
    if query:
        if query.startswith(" & "):
            query = query[3:]
        df_results = df_results.query(query)
    return df_results


def save_results(df_results, output):

    suffixes = "".join(output.suffixes)
    if ".csv" in suffixes:
        sep = ","
    elif ".tsv" in suffixes:
        sep = "\t"
    else:
        s = (
            f"'{suffixes}' not implemented yet, only .csv and .tsv "
            "(and compressed versions)"
        )
        raise AssertionError(s)

    output.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(output, sep=sep, index=False)


def filter_and_save_results(
    output,
    query,
    config_file=None,
    results_dir=None,
    add_fit_predictions=False,
):

    df_results = load_results(
        config_file=config_file,
        results_dir=results_dir,
    )

    df_results = filter_results(df_results, query)

    if add_fit_predictions:
        df_results = append_fit_predictions(df_results)

    save_results(df_results, output)
