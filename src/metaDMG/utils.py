#%%
import warnings
from functools import partial
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
import typer
import yaml
from scipy.stats import betabinom as sp_betabinom


#%%


def path_endswith(path: Path, s: str) -> bool:
    return str(path.name).endswith(s)


def extract_name(
    filename: Path,
    max_length: int = 100,
    prefix: str = "",
    suffix: str = "",
    long_name: bool = False,
) -> str:
    """Extract the name from a file

    Parameters
    ----------
    filename
        The input file
    max_length
        The maximum length of the name, by default 100
    prefix
        The prefix to be added to the name, by default ""
    suffix
        The suffix to be added to the name, by default ""
    long_name
        Whether or not to use the full name, by default False

    Returns
    -------
        The name
    """
    name = Path(filename).stem
    if not long_name:
        name = name.split(".")[0]
    if len(name) > max_length:
        name = name[:max_length] + "..."
    name = prefix + name + suffix
    return name


def extract_names(file_list, **kwargs):
    return list(map(partial(extract_name, **kwargs), file_list))


def extract_alignment_files(paths: list[Path]) -> list[Path]:
    """Extract all alignment files from a list of paths.
    Alignment files are expected to be .bam, .sam, or .sam.gz.

    Parameters
    ----------
    paths
        Input list of paths

    Returns
    -------
        Output list of alignment files
    """
    alignments = []
    suffixes = (".bam", ".sam", ".sam.gz")

    for path in paths:
        # break
        if path.is_file() and any(path_endswith(path, suffix) for suffix in suffixes):
            alignments.append(path)

        elif path.is_dir():

            files = [
                p
                for p in Path(path).glob("*")
                if any(path_endswith(p, suffix) for suffix in suffixes)
            ]

            recursive = extract_alignment_files(files)
            alignments.extend(recursive)

    return alignments


def extract_alignments(
    paths: list[Path],
    prefix: str = "",
    suffix: str = "",
    long_name: bool = False,
) -> dict:
    """Extract all alignment files from a list of files.
    Truncates the name of the files, controlled by prefix, suffix, and long_name

    Parameters
    ----------
    paths
        List of paths to be extracted
    prefix
        The prefix to be added to the name, by default ""
    suffix
        The suffix to be added to the name, by default ""
    long_name
        Whether or not to use the full name, by default False

    Returns
    -------
        Dictionary with names as keys and files as values.
    """

    alignments = extract_alignment_files(paths)
    samples = extract_names(
        alignments,
        prefix=prefix,
        suffix=suffix,
        long_name=long_name,
    )

    d_alignments = {}
    for sample, path in zip(samples, alignments):
        d_alignments[sample] = str(path)

    return d_alignments


def paths_to_strings(
    d: dict,
    ignore_keys: Optional[Iterable] = None,
) -> dict:
    """Convert all the paths in a dictionary to strings

    Parameters
    ----------
    d
        Input dict to be converted
    ignore_keys
        Ignore the following keys in the iterable, by default None

    Returns
    -------
        Dictionary with strings instead of paths
    """

    if ignore_keys is None:
        ignore_keys = []

    d_out = {}
    for key, val in d.items():
        if val in ignore_keys:
            continue
        elif isinstance(val, list):
            d_out[key] = list(map(str, val))
        elif isinstance(val, tuple):
            d_out[key] = tuple(map(str, val))
        elif isinstance(val, dict):
            d_out[key] = paths_to_strings(val)
        elif isinstance(val, Path):
            d_out[key] = str(val)
        else:
            d_out[key] = val
    return d_out


#%%


def save_config_file(config: dict, config_path: Path) -> None:
    """Save the config file.
    Does not overwrite if file already exists, unless explicitly specified.

    Parameters
    ----------
    config
        _description_
    config_path
        _description_

    Raises
    ------
    typer.Abort
        _description_
    """

    if config_path.is_file():
        s = "Config file already exists. Do you want to overwrite it?"
        overwrite = typer.confirm(s)
        if not overwrite:
            typer.echo("Exiting")
            raise typer.Abort()

    with open(config_path, "w") as file:
        yaml.dump(config, file, sort_keys=False)
    typer.echo("Config file was created")


#%%


def check_metaDMG_fit():
    try:
        import metaDMG.fit

    except ModuleNotFoundError:
        print("""The 'fit' extras has to be installed: pip install "metaDMG[fit]" """)
        raise typer.Abort()


def check_metaDMG_viz():
    try:
        import metaDMG.viz

    except ModuleNotFoundError:
        print("""The 'viz' extras has to be installed: pip install "metaDMG[viz]" """)
        raise typer.Abort()


#%%


def get_results_dir(
    config_path: Optional[Path] = None,
    results_dir: Optional[Path] = None,
) -> Path:
    """Helper function that gets the results directory from either the
    config file or the results directory directly.

    Parameters
    ----------
    config_path
        Config file, by default None
    results_dir
        Results directory, by default None

    Returns
    -------
        Path to the results directory

    Raises
    ------
    AssertionError
        If both config file and results directory are set, raise error
    """

    if config_path is not None and results_dir is not None:
        raise AssertionError("'config_path' and 'results_dir' cannot both be set")

    if results_dir:
        return results_dir

    if config_path is None:
        config_path = Path("config.yaml")

    with open(config_path, "r") as file:
        d = yaml.safe_load(file)

    return Path(d["dir"]) / "results"


#%%


def get_single_fit_prediction(df_results):

    Bayesian = any(["Bayesian" in column for column in df_results.columns])

    if Bayesian:
        prefix = "Bayesian_"
    else:
        prefix = ""

    A = df_results[f"{prefix}A"].values
    q = df_results[f"{prefix}q"].values
    c = df_results[f"{prefix}c"].values
    phi = df_results[f"{prefix}phi"].values

    max_position = max(
        int(name.split("+")[1]) for name in df_results.columns if name.startswith("k+")
    )

    x = np.hstack(
        [np.arange(max_position) + 1, np.arange(-1, -max_position - 1, -1)]
    ).reshape((-1, 1))

    mask_N = [
        (name.startswith("N+") or name.startswith("N-")) for name in df_results.columns
    ]
    N = df_results.iloc[:, mask_N].values

    Dx = A * (1 - q) ** (np.abs(x) - 1) + c

    alpha = Dx * phi
    beta = (1 - Dx) * phi

    dist = sp_betabinom(n=N, a=alpha.T, b=beta.T)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        std = dist.std() / N

    std[np.isnan(std)] = 0

    df_Dx = pd.concat(
        (
            # pd.DataFrame(df_results.tax_id, columns=["tax_id"]),
            pd.DataFrame(Dx.T, columns=[f"Dx{xi:+}" for xi in x.flatten()]),
            pd.DataFrame(std, columns=[f"Dx_std{xi:+}" for xi in x.flatten()]),
        ),
        axis=1,
    )

    return df_Dx


def append_fit_predictions(df_results):
    df_Dx = get_single_fit_prediction(df_results)
    return pd.concat((df_results.reset_index(drop=True), df_Dx), axis=1)
