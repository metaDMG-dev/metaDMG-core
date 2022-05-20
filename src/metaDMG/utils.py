#%%
import re
import warnings
from functools import partial
from itertools import islice
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union

import numpy as np
import pandas as pd
import psutil
import typer
import yaml
from logger_tt import logger
from scipy.stats import betabinom as sp_betabinom


#%%


class Config(dict):
    """Config contains the parameters related to specific alignment file."""

    pass


class Configs(dict):
    """Configs contains the parameters related to config file.
    Inherits from dict. Implements iterations.
    """

    def __iter__(self) -> Iterator[Config]:
        """Iteration

        Yields
        ------
        Iterator[Config]
            Allow for iteration
        """
        dir_lca = self["output_dir"] / "lca"
        dir_pmd = self["output_dir"] / "pmd"
        samples = self["samples"].keys()
        for sample in samples:
            config = Config(self)
            config["sample"] = sample
            config["bam"] = config["samples"][sample]

            config["path_mismatches_txt"] = dir_lca / f"{sample}.mismatches.txt.gz"

            if config["damage_mode"] == "lca":
                config["path_mismatches_stat"] = (
                    dir_lca / f"{sample}.mismatches.stat.txt.gz"
                )
            else:
                config["path_mismatches_stat"] = dir_lca / f"{sample}.stat.txt"

            config["path_lca"] = dir_lca / f"{sample}.lca.txt.gz"
            config["path_lca_log"] = dir_lca / f"{sample}.log.txt"
            config["path_tmp"] = config["output_dir"] / "tmp" / sample

            config["path_pmd"] = dir_pmd / f"{sample}.pmd.txt.gz"

            yield config

    def get_nth(self, n: int) -> Config:
        """Gets the n'th config

        Parameters
        ----------
        n
            The index

        Returns
        -------
        Config
            A single configuration
        """
        return next(islice(self, n, None))

    def get_first(self) -> Config:
        """Get the first config

        Returns
        -------
        Config
            A single configuration
        """
        return self.get_nth(n=0)

    def __len__(self) -> int:
        """The number of configs

        Returns
        -------
        int
            The number of configs
        """
        return len(self["samples"].keys())

    def check_number_of_jobs(self) -> None:
        """Compare the number of configs to the number of parallel_samples used."""

        parallel_samples = min(self["parallel_samples"], len(self["samples"]))
        cores_per_sample = self["cores_per_sample"]
        N_jobs = parallel_samples * cores_per_sample
        max_cores = psutil.cpu_count(logical=True)
        max_cores_real = psutil.cpu_count(logical=False)

        if N_jobs > max_cores:
            logger.warning(
                f"The total number of jobs {N_jobs} are higher "
                f"than the number of parallel_samples {max_cores}. "
                f"Do not do this unless you know what you are doing. "
                f"Try decreasing either 'parallel_samples' or 'parallel_samples-per-sample'."
            )
        elif N_jobs > max_cores_real:
            logger.info(
                f"The total number of jobs {N_jobs} are higher "
                f"than the real number of parallel_samples {max_cores_real} (non-logical). "
                f"This might decrease performance. "
            )


def make_configs(
    config_file: Optional[Path],
    log_port: Optional[int] = None,
    log_path: Optional[str] = None,
    force: bool = False,
) -> Configs:
    """Create an instance of Configs from a config file

    Parameters
    ----------
    config_file
        The config file to load
    log_port
        Optional log port, by default None
    log_path
        Optional log path, by default None
    force
        Whether or not the computations are force, by default False

    Returns
    -------
        An instance of Configs

    Raises
    ------
    typer.Abort
        If not a proper config file
    """

    if config_file is None:
        config_file = Path("config.yaml")

    if not config_file.exists():
        logger.error("Error! Please select a proper config file!")
        raise typer.Abort()

    logger.info(f"Using {config_file} as config file.")
    with open(config_file, "r") as file:
        d = yaml.safe_load(file)

    d = update_old_config(d)

    d["log_port"] = log_port
    d["log_path"] = log_path

    d.setdefault("forward_only", False)
    d.setdefault("cores_per_sample", 1)
    d.setdefault("damage_mode", "lca")
    d["force"] = force

    paths = ["names", "nodes", "acc2tax", "output_dir", "config_file"]
    for path in paths:
        if d[path]:
            d[path] = Path(d[path])
    for key, val in d["samples"].items():
        d["samples"][key] = Path(val)

    for key, val in d.items():
        if isinstance(val, str):
            if val.isdigit():
                d[key] = int(key)

    d["custom_database"] = 0 if d["custom_database"] else 1

    return Configs(d)


#%%


def update_old_config(d: dict) -> dict:

    if "version" in d:
        # new version, not changing anything
        return d

    logger.warning(
        "Using an old version of the config file. Please remake the config file."
    )

    d_old2new = {
        "metaDMG-lca": "metaDMG_cpp",
        "minmapq": "min_mapping_quality",
        "editdistmin": "min_edit_dist",
        "editdistmax": "max_edit_dist",
        "simscorelow": "min_similarity_score",
        "simscorehigh": "max_similarity_score",
        "weighttype": "weight_type",
        "storage_dir": "output_dir",
        "dir": "output_dir",
        "fix_ncbi": "custom_database",
        "cores": "parallel_samples",
        "cores_per_sample": "cores_per_sample",
        "config_path": "config_file",
    }

    d_new = {}
    for key, value in d.items():
        if key in d_old2new:
            key = d_old2new[key]
        d_new[key] = value
    d_new.pop("forced")

    return d_new


#%%


# def remove_file(file: Path | str, missing_ok: bool = False) -> None:
def remove_file(file: Union[Path, str], missing_ok: bool = False) -> None:
    Path(file).unlink(missing_ok=missing_ok)


# def remove_directory(path: Path | str, missing_ok: bool = False) -> None:
def remove_directory(path: Union[Path, str], missing_ok: bool = False) -> None:
    """Remove everything in a directory

    Parameters
    ----------
    path
        Directory to be deleted
    """

    try:
        path = Path(path)
        for child in path.iterdir():
            if child.is_file():
                remove_file(child)
            else:
                remove_directory(child)
        path.rmdir()
    except FileNotFoundError:
        if not missing_ok:
            raise


#%%


def split_string(s: str) -> list[str]:
    """Split a string by comma, space, or both.

    Parameters
    ----------
    s
        Input string

    Returns
    -------
        List of strings
    """
    return re.findall(r"[^,\s]+", s)


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


def extract_samples(
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


def save_config_file(
    config: dict,
    config_file: Path,
    overwrite_config: bool = False,
) -> None:
    """Save the config file.
    Does not overwrite if file already exists, unless explicitly specified.

    Parameters
    ----------
    config
        Input dict
    config_file
        Save location

    Raises
    ------
    typer.Abort
        Do not overwrite automatically
    """

    if not overwrite_config:
        if config_file.is_file():
            s = "Config file already exists. Do you want to overwrite it?"
            confirmed = typer.confirm(s)
            if not confirmed:
                typer.echo("Exiting")
                raise typer.Abort()

    with open(config_file, "w") as file:
        yaml.dump(config, file, sort_keys=False)
    typer.echo(f"{str(config_file)} was created")


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
    config_file: Optional[Path] = None,
    results_dir: Optional[Path] = None,
) -> Path:
    """Helper function that gets the results directory from either the
    config file or the results directory directly.

    Parameters
    ----------
    config_file
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

    if config_file is not None and results_dir is not None:
        raise AssertionError("'config_file' and 'results_dir' cannot both be set")

    if results_dir:
        return results_dir

    if config_file is None:
        config_file = Path("config.yaml")

    configs = make_configs(config_file)

    return configs["output_dir"] / "results"


#%%


def get_single_fit_prediction(df_results):

    Bayesian = any(["Bayesian" in column for column in df_results.columns])

    if Bayesian:
        prefix = "Bayesian_"
    else:
        prefix = ""

    if "k-1" in df_results.columns:
        forward_only = False
    else:
        forward_only = True

    A = df_results[f"{prefix}A"].values
    q = df_results[f"{prefix}q"].values
    c = df_results[f"{prefix}c"].values
    phi = df_results[f"{prefix}phi"].values

    max_position = max(
        int(name.split("+")[1]) for name in df_results.columns if name.startswith("k+")
    )

    if forward_only:
        x = np.arange(max_position) + 1
    else:
        x = np.hstack(
            [np.arange(max_position) + 1, np.arange(-1, -max_position - 1, -1)]
        )
    x = x.reshape((-1, 1))

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


#%%


def run_PMD(config: Config):
    """Run the PMD command from metaDMG-cpp and output the result to the gzipped txt_out

    Parameters
    ----------
    alignment_file
        Alignment file to compute the PMD scores on
    txt_out
        The (gzipped) output txt file
    """

    import gzip
    import shlex
    import subprocess

    txt_out = config["path_pmd"]
    txt_out.parent.mkdir(parents=True, exist_ok=True)

    with gzip.open(f"{txt_out}", "wt") as zip_out:

        cpp = subprocess.Popen(
            shlex.split(f"{config['metaDMG_cpp']} pmd {config['bam']}"),
            stdout=subprocess.PIPE,
        )

        zip = subprocess.Popen(
            ["gzip"],
            stdin=cpp.stdout,
            stdout=zip_out,
        )
        zip.communicate()
