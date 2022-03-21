import math
from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd
import yaml
from iminuit import describe
from numba import njit
from scipy.special import erf, erfinv
from scipy.stats import chi2 as sp_chi2


#%%

ACTG = ["A", "C", "G", "T"]

ref_obs_bases = []
for ref in ACTG:
    for obs in ACTG:
        ref_obs_bases.append(f"{ref}{obs}")

#%%

from itertools import islice
from typing import Iterable, Iterator, Optional

import psutil
import typer
from logger_tt import logger


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

    # updating the old version

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


def downcast_dataframe(df, categories=None, fully_automatic=False):

    if categories is None:
        categories = []

    categories = [category for category in categories if category in df.columns]

    d_categories = {category: "category" for category in categories}
    df2 = df.astype(d_categories)

    int_cols = df2.select_dtypes(include=["integer"]).columns

    if df2[int_cols].max().max() > np.iinfo("uint32").max:
        raise AssertionError("Dataframe contains too large values.")

    for col in int_cols:
        if fully_automatic:
            df2.loc[:, col] = pd.to_numeric(df2[col], downcast="integer")
        else:
            if col == "position":
                df2.loc[:, col] = df2[col].astype("int8")
            else:
                df2.loc[:, col] = df2[col].astype("uint32")

    for col in df2.select_dtypes(include=["float"]).columns:
        if fully_automatic:
            df2.loc[:, col] = pd.to_numeric(df2[col], downcast="float")
        else:
            df2.loc[:, col] = df2[col].astype("float32")

    return df2


#%%


def is_forward(df):
    return df["direction"] == "5'"


def get_forward(df):
    s = "5'"
    return df.query("direction == @s")


def get_priors():

    # beta
    A_prior = mu_phi_to_alpha_beta(mu=0.2, phi=5)  # mean = 0.2, concentration = 5
    q_prior = mu_phi_to_alpha_beta(mu=0.2, phi=5)  # mean = 0.2, concentration = 5
    c_prior = mu_phi_to_alpha_beta(mu=0.1, phi=10)  # mean = 0.1, concentration = 10

    # exponential (min, scale)
    phi_prior = (2, 1000)

    return {
        "A": A_prior,
        "q": q_prior,
        "c": c_prior,
        "phi": phi_prior,
    }


#%%


def prob_to_z(p):
    return np.sqrt(2) * erfinv(p)


def z_to_prob(z):
    return erf(z / np.sqrt(2))


def compute_likelihood_ratio(frequentist_PMD, frequentist_null):
    LR = -2 * (frequentist_PMD.log_likelihood - frequentist_null.log_likelihood)

    df = len(describe(frequentist_PMD)) - len(describe(frequentist_null))
    LR_P = sp_chi2.sf(x=LR, df=df)
    LR_z = prob_to_z(1 - LR_P)

    return LR, LR_P, LR_z


def sample_from_param_grid(param_grid, random_state=None):
    np.random.seed(42)
    parameters = {}
    for key, dist in param_grid.items():
        parameters[key] = dist.rvs(random_state=random_state)
    return parameters


def alpha_beta_to_mu_phi(alpha, beta):
    mu = alpha / (alpha + beta)
    phi = alpha + beta
    return mu, phi


def mu_phi_to_alpha_beta(mu, phi):
    alpha = mu * phi
    beta = phi * (1 - mu)
    return alpha, beta


#%%


@njit
def gammaln_scalar(x):
    return math.lgamma(x)


@njit
def gammaln_vec(xs):
    out = np.empty(len(xs), dtype="float")
    for i, x in enumerate(xs):
        out[i] = math.lgamma(x)
    return out


@njit
def log_betabinom_PMD(k, N, alpha, beta):
    return (
        gammaln_vec(N + 1)  # type: ignore
        + gammaln_vec(k + alpha)
        + gammaln_vec(N - k + beta)
        + gammaln_vec(alpha + beta)
        - (
            gammaln_vec(k + 1)
            + gammaln_vec(N - k + 1)
            + gammaln_vec(alpha)
            + gammaln_vec(beta)
            + gammaln_vec(N + alpha + beta)
        )
    )


@njit
def xlog1py(x, y):
    if x == 0:
        return 0

    return x * np.log1p(y)


@njit
def xlogy(x, y):
    if x == 0:
        return 0

    return x * np.log(y)


@njit
def betaln(x, y):
    return gammaln_scalar(x) + gammaln_scalar(y) - gammaln_scalar(x + y)


@njit
def log_beta(x, alpha, beta):
    lPx = xlog1py(beta - 1.0, -x) + xlogy(alpha - 1.0, x)
    lPx -= betaln(alpha, beta)
    return lPx


@njit
def log_exponential(x, loc, scale):
    if x < loc:
        return -np.inf
    return -(x - loc) / scale - np.log(scale)


#%%


@njit
def log_betabinom_null(k, N, alpha, beta):
    return (
        gammaln_vec(N + 1)
        + gammaln_vec(k + alpha)
        + gammaln_vec(N - k + beta)
        + gammaln_scalar(alpha + beta)
        - (
            gammaln_vec(k + 1)
            + gammaln_vec(N - k + 1)
            + gammaln_scalar(alpha)
            + gammaln_scalar(beta)
            + gammaln_vec(N + alpha + beta)
        )
    )
