#%%
import numpy as np
from iminuit import Minuit
from logger_tt import logger
from numba import njit
from scipy.stats import beta as sp_beta
from scipy.stats import betabinom as sp_betabinom
from scipy.stats import expon as sp_exponential

from metaDMG.fit import fit_utils


#%%

priors = fit_utils.get_priors()
q_prior = priors["q"]  # mean = 0.2, concentration = 5
A_prior = priors["A"]  # mean = 0.2, concentration = 5
c_prior = priors["c"]  # mean = 0.1, concentration = 10
phi_prior = priors["phi"]

#%%


@njit
def compute_log_likelihood(A, q, c, phi, x, k, N):
    Dx = A * (1 - q) ** (np.abs(x) - 1) + c
    alpha = Dx * phi
    beta = (1 - Dx) * phi
    return -fit_utils.log_betabinom_PMD(k=k, N=N, alpha=alpha, beta=beta).sum()


@njit
def compute_log_prior(A, q, c, phi):
    lp = (
        fit_utils.log_beta(A, *A_prior)
        + fit_utils.log_beta(q, *q_prior)
        + fit_utils.log_beta(c, *c_prior)
        + fit_utils.log_exponential(phi, *phi_prior)
    )
    return -lp


@njit
def compute_log_posterior(A, q, c, phi, x, k, N):
    log_likelihood = compute_log_likelihood(A=A, q=q, c=c, phi=phi, x=x, k=k, N=N)
    log_p = compute_log_prior(A=A, q=q, c=c, phi=phi)
    return log_likelihood + log_p


#%%


class Frequentist:
    def __init__(
        self,
        data,
        sample,
        tax_id,
        method="posterior",
        p0=None,
        verbose=False,
    ):
        self.sample = sample
        self.tax_id = tax_id
        self.x = data["x"]
        self.k = data["k"]
        self.N = data["N"]
        self.method = method
        self.verbose = verbose
        self._setup_p0(p0)
        self._setup_minuit()
        self.is_fitted = False

    def __repr__(self):
        s = f"Frequentist(data, method={self.method}). \n"
        if self.is_fitted:
            s += self.__str__()
        return s

    def __str__(self):
        if self.is_fitted:
            s = f"sample = {self.sample}, tax_id = {self.tax_id} \n"
            s += f"A = {self.A:.3f}, q = {self.q:.3f},"
            s += f"c = {self.c:.5f}, phi = {self.phi:.1f} \n"
            s += f"damage = {self.damage:.3f} +/- {self.damage_std:.3f} \n"
            s += f"significance = {self.significance:.3f} \n"
            s += f"rho_Ac = {self.rho_Ac:.3f} \n"
            s += f"log_likelihood = {self.log_likelihood:.3f} \n"
            s += f"valid = {self.valid}"
            return s
        else:
            return f"Frequentist(data, method={self.method}, is_fitted=False). \n\n"

    def __call__(self, A, q, c, phi):
        if self.method == "likelihood":
            return self.compute_log_likelihood(
                A=A,
                q=q,
                c=c,
                phi=phi,
            )
        elif self.method == "posterior":
            return self.compute_log_posterior(
                A=A,
                q=q,
                c=c,
                phi=phi,
            )

    def compute_log_likelihood(self, A, q, c, phi):
        return compute_log_likelihood(
            A=A,
            q=q,
            c=c,
            phi=phi,
            x=self.x,
            k=self.k,
            N=self.N,
        )

    def compute_log_posterior(self, A, q, c, phi):
        return compute_log_posterior(
            A=A,
            q=q,
            c=c,
            phi=phi,
            x=self.x,
            k=self.k,
            N=self.N,
        )

    def _setup_p0(self, p0):
        if p0 is None:
            self.p0 = dict(q=0.1, A=0.1, c=0.01, phi=1000)
        else:
            self.p0 = p0

        self.param_grid = {
            "A": sp_beta(*A_prior),
            "q": sp_beta(*q_prior),
            "c": sp_beta(*c_prior),
            "phi": sp_exponential(*phi_prior),
        }

    def _setup_minuit(self, m=None):

        if self.method == "likelihood":
            f = self.compute_log_likelihood

        elif self.method == "posterior":
            f = self.compute_log_posterior

        if m is None:
            self.m = Minuit(f, **self.p0)
        else:
            self.m = m

        if self.method == "likelihood":
            self.m.limits["A"] = (0, 1)
            self.m.limits["q"] = (0, 1)
            self.m.limits["c"] = (0, 1)

        elif self.method == "posterior":
            eps = 1e-10
            self.m.limits["A"] = (0 + eps, 1 - eps)
            self.m.limits["q"] = (0 + eps, 1 - eps)
            self.m.limits["c"] = (0 + eps, 1 - eps)

        self.m.limits["phi"] = (2, None)
        self.m.errordef = Minuit.LIKELIHOOD

    def fit(self):
        if self.verbose:
            print("Initial fit")
        self.m.migrad()
        self.is_fitted = True
        if self.m.valid and self.verbose:
            print("Valid fit")

        # First try to refit it
        if not self.m.valid:
            if self.verbose:
                print("Refitting up to 10 times using last values as p0")
            for i in range(10):
                self.m.migrad()
                if self.m.valid:
                    break
        if self.m.valid and self.verbose:
            print("Valid fit")

        # Then try with a totally flat guess
        if not self.m.valid:
            if self.verbose:
                print("Refitting using a flat p0")
            self._setup_p0({"q": 0.0, "A": 0.0, "c": 0.01, "phi": 100})
            self._setup_minuit()
            self.m.migrad()
        if self.m.valid and self.verbose:
            print("Valid fit")

        # Also try with the default guess
        if not self.m.valid:
            if self.verbose:
                print("Refitting using the default p0")
            self._setup_p0({"q": 0.1, "A": 0.1, "c": 0.01, "phi": 1000})
            self._setup_minuit()
            self.m.migrad()
        if self.m.valid and self.verbose:
            print("Valid fit")

        # If not working, continue with new guesses
        MAX_GUESSES = 100
        if not self.m.valid:

            if self.verbose:
                print("Getting desperate, trying random p0's")

            self.i = 0
            while True:
                p0 = fit_utils.sample_from_param_grid(self.param_grid)
                self._setup_p0(p0)
                self._setup_minuit()
                self.m.migrad()

                if self.m.valid or self.i >= MAX_GUESSES:
                    break
                self.m.migrad()

                if self.m.valid or self.i >= MAX_GUESSES:
                    break

                self.i += 1

        if self.m.valid and self.verbose:
            print(f"Valid fit, number of tries = {self.i}")

        self.valid = self.m.valid

        if self.valid:
            self.damage, self.damage_std, self.significance = self._get_D()
        else:
            self.damage, self.damage_std, self.significance = np.nan, np.nan, np.nan

        return self

    @property
    def log_likelihood(self):
        if self.valid:
            return self.compute_log_likelihood(*self.m.values)
        else:
            return np.nan

    def migrad(self):
        return self.fit()

    def minos(self):
        self.m.minos()
        return self

    @property
    def values(self):
        values = self.m.values.to_dict()
        if self.valid:
            return values
        else:
            for key, val in values.items():
                values[key] = np.nan
            return values

    @property
    def errors(self):
        errors = self.m.errors.to_dict()
        if self.valid:
            return errors
        else:
            for key, val in errors.items():
                errors[key] = np.nan
            return errors

    @property
    def A(self):
        return self.values["A"]

    @property
    def A_std(self):
        return self.errors["A"]

    @property
    def q(self):
        return self.values["q"]

    @property
    def q_std(self):
        return self.errors["q"]

    @property
    def c(self):
        return self.values["c"]

    @property
    def c_std(self):
        return self.errors["c"]

    @property
    def phi(self):
        return self.values["phi"]

    @property
    def phi_std(self):
        return self.errors["phi"]

    def _get_D(self):

        A = self.A
        c = self.c
        phi = self.phi

        N = max(self.N[0], 1)

        mu = A
        std = np.sqrt(A * (1 - A) * (phi + N) / ((phi + 1) * N))
        significance = mu / std
        return mu, std, significance

    @property
    def correlation(self):
        return self.m.covariance.correlation()

    @property
    def rho_Ac(self):
        if self.valid:
            return self.correlation["A", "c"]
        else:
            logger.debug(
                f"Error with: sample = {self.sample}, "
                f"tax_id = {self.tax_id}, "
                f"fit method = {self.method}."
            )
            return np.nan

    @property
    def dist(self):

        A = self.A
        q = self.q
        c = self.c
        phi = self.phi

        x = self.x
        N = self.N

        Dx = A * (1 - q) ** (np.abs(x) - 1) + c

        alpha = Dx * phi
        beta = (1 - Dx) * phi

        dist = sp_betabinom(n=N, a=alpha, b=beta)
        return dist

    @property
    def chi2s(self):
        k = self.k
        dist = self.dist
        chi2s = (dist.mean() - k) ** 2 / dist.std() ** 2
        return chi2s

    @property
    def chi2(self):
        if self.valid:
            return np.sum(self.chi2s)
        else:
            return np.nan


#%%


def make_fits(
    config,
    fit_result,
    data,
    sample,
    tax_id,
    forward_only=None,
    method="posterior",
):
    np.random.seed(42)

    if forward_only is None:
        forward_only = config["forward_only"]

    if forward_only:
        data = {key: val[data["x"] > 0] for key, val in data.items()}

    fit = Frequentist(
        data,
        sample,
        tax_id,
        method=method,
    ).fit()

    vars_to_keep = [
        "damage",
        "damage_std",
        "significance",
        "q",
        "q_std",
        "phi",
        "phi_std",
        "A",
        "A_std",
        "c",
        "c_std",
        "rho_Ac",
        "valid",
    ]

    for var in vars_to_keep:
        fit_result[f"MAP_{var}"] = getattr(fit, var)

    return fit
