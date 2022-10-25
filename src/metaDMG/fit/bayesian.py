#%%
import jax.numpy as jnp
import numpy as np
import numpyro
import pandas as pd
from jax import jit
from jax.random import PRNGKey as Key
from numba import njit
from numpyro import distributions as dist
from numpyro.infer import MCMC, NUTS, Predictive, log_likelihood
from scipy.special import logsumexp
from scipy.stats import beta as sp_beta
from scipy.stats import betabinom as sp_betabinom
from scipy.stats import norm as sp_norm

from metaDMG.fit import fit_utils


#%%

numpyro.enable_x64()

priors = fit_utils.get_priors()
A_prior = priors["A"]  # mean = 0.01, concentration = 1
q_prior = priors["q"]  # mean = 0.2, concentration = 5
c_prior = priors["c"]  # mean = 0.1, concentration = 10
phi_prior = priors["phi"]

#%%


def numpyro_model(x, N, k=None):
    x_abs = jnp.abs(x)

    A = numpyro.sample("A", dist.Beta(A_prior[0], A_prior[1]))
    q = numpyro.sample("q", dist.Beta(q_prior[0], q_prior[1]))
    c = numpyro.sample("c", dist.Beta(c_prior[0], c_prior[1]))
    Dx = jnp.clip(numpyro.deterministic("Dx", A * (1 - q) ** (x_abs - 1) + c), 0, 1)

    delta = numpyro.sample("delta", dist.Exponential(1 / phi_prior[1]))
    phi = numpyro.deterministic("phi", delta + phi_prior[0])

    alpha = numpyro.deterministic("alpha", Dx * phi)
    beta = numpyro.deterministic("beta", (1 - Dx) * phi)

    numpyro.sample("obs", dist.BetaBinomial(alpha, beta, N), obs=k)


#%%


def filter_out_k(data):
    return {key: value for key, value in data.items() if key != "k"}


@jit
def _get_posterior(rng_key, samples, *args, **kwargs):
    return Predictive(numpyro_model, samples)(rng_key, *args, **kwargs)


def get_posterior_predictive(mcmc, data):
    posterior_samples = mcmc.get_samples()
    rng_key = Key(0)
    data_no_k = filter_out_k(data)
    return _get_posterior(rng_key, posterior_samples, **data_no_k)


def get_posterior_predictive_obs(mcmc, data):
    return get_posterior_predictive(mcmc, data)["obs"]


#%%


def get_n_sigma_probability(n_sigma):
    return sp_norm.cdf(n_sigma) - sp_norm.cdf(-n_sigma)


CONF_1_SIGMA = get_n_sigma_probability(1)


def add_D_information(
    fit_result,
    mcmc,
    data,
    prefix="",
):

    A = mcmc.get_samples()["A"]
    phi = mcmc.get_samples()["phi"]
    N = max(data["N"][0], 1)
    mu = np.mean(A)
    std = np.mean(np.sqrt(A * (1 - A) * (phi + N) / ((phi + 1) * N)))

    Dx = A
    alpha = Dx * phi
    beta = (1 - Dx) * phi

    # 1000x faster approximation for sp_betabinom(N, alpha, beta)
    pdf_approx = sp_betabinom(N, alpha.mean(), beta.mean())

    fit_result[f"{prefix}damage"] = mu.item()
    fit_result[f"{prefix}damage_std"] = std.item()
    fit_result[f"{prefix}significance"] = mu.item() / std.item()
    fit_result[f"{prefix}damage_median"] = np.median(A)

    # fit_result[f"{prefix}prob_lt_1p_damage"] = pdf_beta.cdf(0.01).mean()
    # # fit_result[f"{prefix}prob_lt_1p_damage_betabinom"] = pdf.cdf(0.01 * N).mean()
    # fit_result[f"{prefix}prob_zero_damage"] = pdf.cdf(0).mean()

    for n_sigma in [1, 2, 3]:
        conf = get_n_sigma_probability(n_sigma)
        fit_result[f"{prefix}damage_CI_{n_sigma}_sigma_low"] = (
            pdf_approx.ppf((1 - conf) / 2.0).mean() / N
        )
        fit_result[f"{prefix}damage_CI_{n_sigma}_sigma_high"] = (
            pdf_approx.ppf((1 + conf) / 2.0).mean() / N
        )

    fit_result[f"{prefix}damage_CI_95_low"] = (
        pdf_approx.ppf((1 - 0.95) / 2.0).mean() / N
    )
    fit_result[f"{prefix}damage_CI_95_high"] = (
        pdf_approx.ppf((1 + 0.95) / 2.0).mean() / N
    )

    return fit_result


#%%


@jit
def _compute_log_likelihood(posterior_samples, data):
    return log_likelihood(numpyro_model, posterior_samples, **data)["obs"]


def compute_log_likelihood(mcmc, data):
    posterior_samples = mcmc.get_samples()
    return _compute_log_likelihood(posterior_samples, data)


#%%


def add_summary_of_variable(
    fit_result,
    mcmc,
    variable,
    prefix="",
    axis=0,
):
    values = np.array(mcmc.get_samples()[variable])

    s = f"{prefix}{variable}"
    q_low = (1 - CONF_1_SIGMA) / 2.0
    q_high = (1 + CONF_1_SIGMA) / 2.0

    fit_result[f"{s}"] = np.mean(values, axis=axis)
    fit_result[f"{s}_std"] = np.std(values, axis=axis)
    fit_result[f"{s}_median"] = np.median(values, axis=axis)
    fit_result[f"{s}_CI_1_sigma_low"] = np.quantile(values, q_low, axis=axis)
    fit_result[f"{s}_CI_1_sigma_high"] = np.quantile(values, q_high, axis=axis)


def compute_rho_Ac(mcmc):
    A = mcmc.get_samples()["A"]
    c = mcmc.get_samples()["c"]
    return np.corrcoef(A, c)[0, 1]


#%%


def _init_mcmc(model, **kwargs):

    mcmc_kwargs = dict(
        progress_bar=False,
        num_warmup=500,
        num_samples=1000,
        num_chains=1,  # problem when setting to 2
        chain_method="sequential",
        # http://num.pyro.ai/en/stable/_modules/numpyro/infer/mcmc.html#MCMC
    )

    return MCMC(NUTS(model), jit_model_args=True, **mcmc_kwargs, **kwargs)


def init_mcmc(config, **kwargs):
    if config["bayesian"]:
        mcmc = _init_mcmc(numpyro_model, **kwargs)
    else:
        mcmc = None
    return mcmc


def fit_mcmc(mcmc, data, seed=0):
    mcmc.run(Key(seed), **data)


def use_last_state_as_warmup_state(mcmc):
    # https://github.com/pyro-ppl/numpyro/issues/539
    mcmc._warmup_state = mcmc._last_state


def add_Bayesian_fit_result(
    fit_result,
    data,
    mcmc,
):

    add_D_information(fit_result, mcmc, data)

    add_summary_of_variable(fit_result, mcmc, "A")
    add_summary_of_variable(fit_result, mcmc, "q")
    add_summary_of_variable(fit_result, mcmc, "c")
    add_summary_of_variable(fit_result, mcmc, "phi")

    fit_result["rho_Ac"] = compute_rho_Ac(mcmc)


def make_fits(
    fit_result,
    data,
    mcmc,
):
    fit_mcmc(mcmc, data)
    add_Bayesian_fit_result(
        fit_result,
        data,
        mcmc,
    )

    # mcmc.print_summary(prob=0.68)
    # if False:
    #     use_last_state_as_warmup_state(mcmc)
