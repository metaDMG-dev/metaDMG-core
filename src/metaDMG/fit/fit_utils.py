import math
from itertools import islice
from pathlib import Path
from typing import Iterable, Iterator, Optional
from warnings import warn

import numpy as np
import pandas as pd
import typer
import yaml
from iminuit import describe
from logger_tt import logger
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


def get_priors():

    # # beta new
    # A_prior = mu_phi_to_alpha_beta(mu=0.01, phi=1)  # mean = 0.01, concentration = 1
    # q_prior = mu_phi_to_alpha_beta(mu=0.2, phi=5)  # mean = 0.2, concentration = 5
    # c_prior = mu_phi_to_alpha_beta(mu=0.1, phi=10)  # mean = 0.01, concentration = 1

    # beta old
    # A_prior = mu_phi_to_alpha_beta(mu=0.2, phi=5)  # mean = 0.2, concentration = 5
    # q_prior = mu_phi_to_alpha_beta(mu=0.2, phi=5)  # mean = 0.2, concentration = 5
    # c_prior = mu_phi_to_alpha_beta(mu=0.1, phi=10)  # mean = 0.1, concentration = 10

    A_prior = mu_phi_to_alpha_beta(mu=0.1, phi=10)  # mean = 0.1, concentration = 10
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


def alpha_beta_to_mu_phi(alpha, beta):
    mu = alpha / (alpha + beta)
    phi = alpha + beta
    return mu, phi


def mu_phi_to_alpha_beta(mu, phi):
    alpha = mu * phi
    beta = phi * (1 - mu)
    return alpha, beta


#%%


def downcast_dataframe(df, categories=None, fully_automatic=False):

    if categories is None:
        categories = []

    categories = [category for category in categories if category in df.columns]

    d_categories = {category: "category" for category in categories}
    df2 = df.astype(d_categories)

    int_cols = df2.select_dtypes(include=["integer"]).columns

    int_type = "uint32"
    if df2[int_cols].max().max() > np.iinfo("uint32").max:
        int_type = "uint64"
        # raise AssertionError("Dataframe contains too large values.")

    for col in int_cols:
        if fully_automatic:
            df2.loc[:, col] = pd.to_numeric(df2[col], downcast="integer")
        else:
            if col == "position":
                df2.loc[:, col] = df2[col].astype("int8")
            else:
                df2.loc[:, col] = df2[col].astype(int_type)

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


#%%


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


#%%


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
def gammaln_scalar(x):
    return math.lgamma(x)


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
