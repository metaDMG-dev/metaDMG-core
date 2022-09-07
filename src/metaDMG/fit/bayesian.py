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


def model_PMD(x, N, k=None):
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


def model_null(x, N, k=None):
    c = numpyro.sample("c", dist.Beta(c_prior[0], c_prior[1]))
    Dx = numpyro.deterministic("Dx", c)
    delta = numpyro.sample("delta", dist.Exponential(1 / phi_prior[1]))
    phi = numpyro.deterministic("phi", delta + phi_prior[0])

    alpha = numpyro.deterministic("alpha", Dx * phi)
    beta = numpyro.deterministic("beta", (1 - Dx) * phi)

    numpyro.sample("obs", dist.BetaBinomial(alpha, beta, N), obs=k)


#%%


def filter_out_k(data):
    return {key: value for key, value in data.items() if key != "k"}


def is_model_PMD(model):
    name = model.__name__.lower()
    if "pmd" in name:
        return True
    elif "null" in name:
        return False
    raise AssertionError(f"Model should be PMD or null, got {model}")


#%%


@jit
def _get_posterior_PMD(rng_key, samples, *args, **kwargs):
    return Predictive(model_PMD, samples)(rng_key, *args, **kwargs)


@jit
def _get_posterior_null(rng_key, samples, *args, **kwargs):
    return Predictive(model_null, samples)(rng_key, *args, **kwargs)


def get_posterior_predictive(mcmc, data):
    posterior_samples = mcmc.get_samples()
    rng_key = Key(0)
    data_no_k = filter_out_k(data)
    if is_model_PMD(mcmc.sampler.model):
        return _get_posterior_PMD(rng_key, posterior_samples, **data_no_k)
    else:
        return _get_posterior_null(rng_key, posterior_samples, **data_no_k)


def get_posterior_predictive_obs(mcmc, data):
    return get_posterior_predictive(mcmc, data)["obs"]


#%%


def get_n_sigma_probability(n_sigma):
    return sp_norm.cdf(n_sigma) - sp_norm.cdf(-n_sigma)


CONF_1_SIGMA = get_n_sigma_probability(1)


def compute_posterior(
    mcmc, data, func_avg=np.mean, func_dispersion=lambda x: np.std(x, axis=0)
):
    """func = central tendency function, e.g. np.mean or np.median"""
    posterior_predictive = get_posterior_predictive(mcmc, data)
    predictions_fraction = posterior_predictive["obs"] / data["N"]
    y_average = func_avg(predictions_fraction, axis=0)
    # y_dispersion = numpyro.diagnostics.hpdi(predictions_fraction, prob=0.68)
    y_dispersion = func_dispersion(predictions_fraction)
    return y_average, y_dispersion


def compute_D_max(mcmc, data):
    # posterior = get_posterior_predictive(mcmc, data)
    # c = mcmc.get_samples()["c"]
    # f = posterior["obs"] / data["N"]
    # f = f[:, 0]
    # D_max_samples = f - c
    # D_max_mu = np.mean(D_max_samples).item()
    # D_max_std = np.std(D_max_samples).item()

    # New method, more similar to frequentist and better when few reads
    A = mcmc.get_samples()["A"]
    c = mcmc.get_samples()["c"]
    phi = mcmc.get_samples()["phi"]
    N = max(data["N"][0], 1)
    mu = np.mean(A)
    std = np.mean(np.sqrt(A * (1 - A) * (phi + N) / ((phi + 1) * N)))
    # mu.item(), std.item()

    Dx = A
    alpha = Dx * phi
    beta = (1 - Dx) * phi

    # pdf = sp_betabinom(N, alpha, beta)
    pdf = sp_betabinom(N, alpha.mean(), beta.mean())  # 1000x faster approximation
    return {
        "mu": mu.item(),
        "std": std.item(),
        "median": pdf.median().mean() / N,
        "confidence_interval_1_sigma_low": pdf.ppf((1 - CONF_1_SIGMA) / 2.0).mean() / N,
        "confidence_interval_1_sigma_high": pdf.ppf((1 + CONF_1_SIGMA) / 2.0).mean()
        / N,
        "confidence_interval_95_low": pdf.ppf((1 - 0.95) / 2.0).mean() / N,
        "confidence_interval_95_high": pdf.ppf((1 + 0.95) / 2.0).mean() / N,
    }


#%%


@jit
def _compute_log_likelihood_PMD(posterior_samples, data):
    return log_likelihood(model_PMD, posterior_samples, **data)["obs"]


@jit
def _compute_log_likelihood_null(posterior_samples, data):
    return log_likelihood(model_null, posterior_samples, **data)["obs"]


def compute_log_likelihood(mcmc, data):
    posterior_samples = mcmc.get_samples()
    if is_model_PMD(mcmc.sampler.model):
        return _compute_log_likelihood_PMD(posterior_samples, data)
    else:
        return _compute_log_likelihood_null(posterior_samples, data)


#%%


def get_lppd_and_waic(mcmc, data):
    d_results = {}
    # get the log likehood for each (point, num_samples)
    logprob = np.asarray(compute_log_likelihood(mcmc, data))
    # lppd for each observation
    lppd_i = logsumexp(logprob, 0) - np.log(logprob.shape[0])
    d_results["lppd_i"] = lppd_i
    # lppd
    lppd = lppd_i.sum()
    d_results["lppd"] = lppd
    # waic penalty for each observation
    pWAIC_i = np.var(logprob, 0)
    d_results["pWAIC_i"] = pWAIC_i
    # waic penalty # the effective number of parameters penalty
    pWAIC = pWAIC_i.sum()
    d_results["pWAIC"] = pWAIC
    # waic  for each observation
    waic_i = -2 * (lppd_i - pWAIC_i)
    d_results["waic_i"] = waic_i
    # waic # prediction of  out-of-sample deviance
    waic = waic_i.sum()
    d_results["waic"] = waic
    # standard error of waic
    # waic_vec = -2 * (lppd_i - pWAIC_i)
    # waic_uncertainty = jnp.sqrt(logprob.shape[1] * jnp.var(waic_vec))
    return d_results


#%%


# def get_mean_of_variable(mcmc, variable, axis=0):
#     values = mcmc.get_samples()[variable]
#     return np.mean(values, axis=axis).item()


# def get_std_of_variable(mcmc, variable, axis=0):
#     values = mcmc.get_samples()[variable]
#     return np.std(values, axis=axis).item()


def add_summary_of_variable(
    fit_result,
    mcmc,
    variable,
    prefix="Bayesian_",
    axis=0,
):
    values = np.array(mcmc.get_samples()[variable])

    s = f"{prefix}{variable}"
    q_low = (1 - CONF_1_SIGMA) / 2.0
    q_high = (1 + CONF_1_SIGMA) / 2.0

    fit_result[f"{s}"] = np.mean(values, axis=axis)
    fit_result[f"{s}_std"] = np.std(values, axis=axis)
    fit_result[f"{s}_median"] = np.median(values, axis=axis)
    fit_result[f"{s}_confidence_interval_1_sigma_low"] = np.quantile(
        values, q_low, axis=axis
    )
    fit_result[f"{s}_confidence_interval_1_sigma_high"] = np.quantile(
        values, q_high, axis=axis
    )


def compute_rho_Ac(mcmc):
    A = mcmc.get_samples()["A"]
    c = mcmc.get_samples()["c"]
    return np.corrcoef(A, c)[0, 1]


@njit
def compute_dse(waic_i_x, waic_i_y):
    N = len(waic_i_x)
    return np.sqrt(N * np.var(waic_i_x - waic_i_y))


@njit
def compute_z_from_waic_is(waic_i_x, waic_i_y):
    dse = compute_dse(waic_i_x, waic_i_y)
    d_waic = waic_i_y.sum() - waic_i_x.sum()
    z = d_waic / dse
    return z


def compute_z(d_results_PMD, d_results_null):
    z = compute_z_from_waic_is(d_results_PMD["waic_i"], d_results_null["waic_i"])
    return z


@njit
def compute_z_jackknife_error_from_waic_is(waic_i_x, waic_i_y):
    N = len(waic_i_x)
    all_ids = np.arange(N)
    zs = np.empty(N)
    for i in range(N):
        mask = all_ids != i
        zs[i] = compute_z_from_waic_is(waic_i_x[mask], waic_i_y[mask])
    z_jack_std = np.std(zs)
    return z_jack_std


def compute_z_jackknife_error(d_results_PMD, d_results_null):
    return compute_z_jackknife_error_from_waic_is(
        d_results_PMD["waic_i"],
        d_results_null["waic_i"],
    )


#%%


def init_mcmc(model, **kwargs):

    mcmc_kwargs = dict(
        progress_bar=False,
        num_warmup=500,
        num_samples=1000,
        num_chains=1,  # problem when setting to 2
        chain_method="sequential",
        # http://num.pyro.ai/en/stable/_modules/numpyro/infer/mcmc.html#MCMC
    )

    return MCMC(NUTS(model), jit_model_args=True, **mcmc_kwargs, **kwargs)


def init_mcmc_PMD(**kwargs):
    mcmc_PMD = init_mcmc(model_PMD, **kwargs)
    return mcmc_PMD


def init_mcmc_null(**kwargs):
    mcmc_null = init_mcmc(model_null, **kwargs)
    return mcmc_null


def init_mcmcs(config, **kwargs):
    if config["bayesian"]:
        mcmc_PMD = init_mcmc_PMD(**kwargs)
        mcmc_null = init_mcmc_null(**kwargs)
    else:
        mcmc_PMD = None
        mcmc_null = None
    return mcmc_PMD, mcmc_null


def fit_mcmc(mcmc, data, seed=0):
    mcmc.run(Key(seed), **data)


def use_last_state_as_warmup_state(mcmc):
    # https://github.com/pyro-ppl/numpyro/issues/539
    mcmc._warmup_state = mcmc._last_state


def add_Bayesian_fit_result(
    fit_result,
    data,
    mcmc_PMD,
    mcmc_null,
):

    d_results_PMD = get_lppd_and_waic(mcmc_PMD, data)
    d_results_null = get_lppd_and_waic(mcmc_null, data)

    z = compute_z(d_results_PMD, d_results_null)
    fit_result["Bayesian_z"] = z

    D_max = compute_D_max(mcmc_PMD, data)
    fit_result["Bayesian_D_max"] = D_max["mu"]
    fit_result["Bayesian_D_max_std"] = D_max["std"]
    fit_result["Bayesian_D_max_median"] = D_max["median"]
    fit_result["Bayesian_D_max_confidence_interval_1_sigma_low"] = D_max[
        "confidence_interval_1_sigma_low"
    ]
    fit_result["Bayesian_D_max_confidence_interval_1_sigma_high"] = D_max[
        "confidence_interval_1_sigma_high"
    ]
    fit_result["Bayesian_D_max_confidence_interval_95_low"] = D_max[
        "confidence_interval_95_low"
    ]
    fit_result["Bayesian_D_max_confidence_interval_95_high"] = D_max[
        "confidence_interval_95_high"
    ]

    add_summary_of_variable(fit_result, mcmc_PMD, "A")
    add_summary_of_variable(fit_result, mcmc_PMD, "q")
    add_summary_of_variable(fit_result, mcmc_PMD, "c")
    add_summary_of_variable(fit_result, mcmc_PMD, "phi")

    fit_result["Bayesian_rho_Ac"] = compute_rho_Ac(mcmc_PMD)


def make_fits(fit_result, data, mcmc_PMD, mcmc_null):
    fit_mcmc(mcmc_PMD, data)
    fit_mcmc(mcmc_null, data)
    add_Bayesian_fit_result(fit_result, data, mcmc_PMD, mcmc_null)
    # mcmc_PMD.print_summary(prob=0.68)
    # mcmc_null.print_summary(prob=0.68)

    # if False:
    #     use_last_state_as_warmup_state(mcmc_PMD)
    #     use_last_state_as_warmup_state(mcmc_null)
