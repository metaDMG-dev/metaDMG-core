from pathlib import Path
from metaDMG.utils import load_config, get_results_dir
import pandas as pd
from metaDMG.fit.results import append_fit_predictions


def load_results(config_path=None, results_dir=None):
    results_dir = get_results_dir(
        config_path=config_path,
        results_dir=results_dir,
    )
    df_results = pd.read_parquet(results_dir)
    return df_results


def filter_results(df_results, query):
    if query:
        df_results = df_results.query(query)
    return df_results


def save_results(df_results, output):

    suffix = output.suffix
    if suffix == ".csv":
        sep = ","
    elif suffix == ".tsv":
        sep = r"\t"
    else:
        raise AssertionError(f"'{suffix}' not implemented yet, only .csv and .tsv.")

    output.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(output, sep=sep, index=False)


def filter_and_save_results(
    output,
    query,
    config_path=None,
    results_dir=None,
    add_fit_predictions=False,
):

    df_results = load_results(
        config_path=config_path,
        results_dir=results_dir,
    )

    df_results = filter_results(df_results, query)

    if add_fit_predictions:
        df_results = append_fit_predictions(df_results)

    save_results(df_results, output)
