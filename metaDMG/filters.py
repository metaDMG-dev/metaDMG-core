from pathlib import Path


def load_results(config=None, results_dir=None):

    if config is not None and results_dir is not None:
        raise AssertionError(
            "Only a single one of 'config' and 'results_dir' can be set"
        )

    from metaDMG.utils import load_config
    import pandas as pd

    if results_dir is not None:
        pass

    else:
        results_dir = Path(load_config(config)["dir"]) / "results"

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


def filter_and_save_results(output, query, config=None, results_dir=None):

    df_results = load_results(
        config=config,
        results_dir=results_dir,
    )

    df_results = filter_results(df_results, query)
    save_results(df_results, output)
