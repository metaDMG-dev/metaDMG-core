import numpy as np
from iminuit import Minuit
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
def log_likelihood_PMD(A, q, c, phi, x, k, N):
    Dx = A * (1 - q) ** (np.abs(x) - 1) + c
    alpha = Dx * phi
    beta = (1 - Dx) * phi
    return -fit_utils.log_betabinom_PMD(k=k, N=N, alpha=alpha, beta=beta).sum()


@njit
def log_prior_PMD(A, q, c, phi):
    lp = (
        fit_utils.log_beta(A, *A_prior)
        + fit_utils.log_beta(q, *q_prior)
        + fit_utils.log_beta(c, *c_prior)
        + fit_utils.log_exponential(phi, *phi_prior)
    )
    return -lp


@njit
def log_posterior_PMD(A, q, c, phi, x, k, N):
    log_likelihood = log_likelihood_PMD(A=A, q=q, c=c, phi=phi, x=x, k=k, N=N)
    log_p = log_prior_PMD(A=A, q=q, c=c, phi=phi)
    return log_likelihood + log_p


#%%


class FrequentistPMD:
    def __init__(self, data, method="posterior"):
        self.x = data["x"]
        self.k = data["k"]
        self.N = data["N"]
        self.method = method
        self._setup_p0()
        self._setup_minuit()
        self.is_fitted = False

    def __repr__(self):
        s = f"FrequentistPMD(data, method={self.method}). \n\n"
        if self.is_fitted:
            s += self.__str__()
        return s

    def __str__(self):
        if self.is_fitted:
            s = f"A = {self.A:.3f}, q = {self.q:.3f},"
            s += f"c = {self.c:.5f}, phi = {self.phi:.1f} \n"
            s += f"D_max = {self.D_max:.3f} +/- {self.D_max_std:.3f} \n"
            s += f"rho_Ac = {self.rho_Ac:.3f} \n"
            s += f"log_likelihood = {self.log_likelihood:.3f} \n"
            s += f"valid = {self.valid}"
            return s
        else:
            return f"FrequentistPMD(data, method={self.method}). \n\n"

    def __call__(self, A, q, c, phi):
        if self.method == "likelihood":
            return self.log_likelihood_PMD(
                A=A,
                q=q,
                c=c,
                phi=phi,
            )
        elif self.method == "posterior":
            return self.log_posterior_PMD(
                A=A,
                q=q,
                c=c,
                phi=phi,
            )

    def log_likelihood_PMD(self, A, q, c, phi):
        return log_likelihood_PMD(
            A=A,
            q=q,
            c=c,
            phi=phi,
            x=self.x,
            k=self.k,
            N=self.N,
        )

    def log_posterior_PMD(self, A, q, c, phi):
        return log_posterior_PMD(
            A=A,
            q=q,
            c=c,
            phi=phi,
            x=self.x,
            k=self.k,
            N=self.N,
        )

    def _setup_p0(self):
        self.p0 = dict(q=0.1, A=0.1, c=0.01, phi=1000)
        self.param_grid = {
            "A": sp_beta(*A_prior),  # mean = 0.2, shape = 4
            "q": sp_beta(*q_prior),  # mean = 0.2, shape = 4
            "c": sp_beta(*c_prior),  # mean = 0.1, shape = 10
            "phi": sp_exponential(*phi_prior),
        }

    def _setup_minuit(self, m=None):

        if self.method == "likelihood":
            f = self.log_likelihood_PMD

        elif self.method == "posterior":
            f = self.log_posterior_PMD

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
        self.m.migrad()
        self.is_fitted = True

        # first time try to reinitialise with previous fit result
        if not self.m.valid:
            self.m.migrad()

        # if not working, continue with new guesses
        if not self.m.valid:
            self.i = 0
            while True:
                p0 = fit_utils.sample_from_param_grid(self.param_grid)
                for key, val in p0.items():
                    self.m.values[key] = val
                self.m.migrad()
                if self.m.valid or self.i >= 100:
                    break
                self.m.migrad()
                if self.m.valid or self.i >= 100:
                    break
                self.i += 1

        self.valid = self.m.valid
        self._set_D_max()
        return self

    @property
    def log_likelihood(self):
        return self.log_likelihood_PMD(*self.values)

    def migrad(self):
        return self.fit()

    def minos(self):
        self.m.minos()
        return self

    @property
    def values(self):
        return self.m.values

    @property
    def A(self):
        return self.m.values["A"]

    @property
    def A_std(self):
        return self.m.errors["A"]

    @property
    def q(self):
        return self.m.values["q"]

    @property
    def q_std(self):
        return self.m.errors["q"]

    @property
    def c(self):
        return self.m.values["c"]

    @property
    def c_std(self):
        return self.m.errors["c"]

    @property
    def phi(self):
        return self.m.values["phi"]

    @property
    def phi_std(self):
        return self.m.errors["phi"]

    def _set_D_max(self):

        A = self.A
        c = self.c
        phi = self.phi

        N = self.N[0]

        mu = A

        if N != 0:
            std = np.sqrt(A * (1 - A) * (phi + N) / ((phi + 1) * N))
        else:
            std = np.nan

        # Dx_x1 = A
        # alpha = Dx_x1 * phi
        # beta = (1 - Dx_x1) * phi

        # dist = sp_betabinom(n=self.N[0], a=alpha, b=beta)

        # # mu = dist.mean() / fit.N[0] - c
        # mu = A
        # if self.N[0] != 0:
        #     std = np.sqrt(dist.var()) / self.N[0]
        # else:
        #     std = np.nan

        self.D_max = mu  # A
        self.D_max_std = std

    @property
    def correlation(self):
        return self.m.covariance.correlation()

    @property
    def rho_Ac(self):
        return self.correlation["A", "c"]

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
        return np.sum(self.chi2s)


#%%


# @njit
# def f_fit_null(c, phi, k, N):
#     alpha = c * phi
#     beta = (1 - c) * phi
#     return -fit_utils.log_betabinom_null(k=k, N=N, alpha=alpha, beta=beta).sum()


@njit
def log_likelihood_null(c, phi, x, k, N):
    alpha = c * phi
    beta = (1 - c) * phi
    return -fit_utils.log_betabinom_null(k=k, N=N, alpha=alpha, beta=beta).sum()


@njit
def log_prior_null(c, phi):
    lp = fit_utils.log_beta(c, *c_prior) + fit_utils.log_exponential(phi, *phi_prior)
    return -lp


@njit
def log_posterior_null(c, phi, x, k, N):
    log_likelihood = log_likelihood_null(c=c, phi=phi, x=x, k=k, N=N)
    log_p = log_prior_null(c=c, phi=phi)
    return log_likelihood + log_p


class FrequentistNull:
    def __init__(self, data, method="posterior"):
        self.x = data["x"]
        self.k = data["k"]
        self.N = data["N"]
        self.method = method
        self._setup_minuit()

    def __call__(self, A, q, c, phi):
        if self.method == "likelihood":
            return self.log_likelihood_null(A=A, q=q, c=c, phi=phi)
        elif self.method == "posterior":
            return self.log_posterior_null(A=A, q=q, c=c, phi=phi)

    def log_likelihood_null(self, c, phi):
        return log_likelihood_null(c=c, phi=phi, x=self.x, k=self.k, N=self.N)

    def log_posterior_null(self, c, phi):
        return log_posterior_null(c=c, phi=phi, x=self.x, k=self.k, N=self.N)

    # def __call__(self, c, phi):
    # return f_fit_null(c, phi, self.k, self.N)

    def _setup_minuit(self):

        if self.method == "likelihood":
            f = self.log_likelihood_null

        elif self.method == "posterior":
            f = self.log_posterior_null

        self.m = Minuit(f, c=0.1, phi=100)

        if self.method == "likelihood":
            self.m.limits["c"] = (0, 1)

        elif self.method == "posterior":
            eps = 1e-10
            self.m.limits["c"] = (0 + eps, 1 - eps)

        self.m.limits["phi"] = (2, None)
        self.m.errordef = Minuit.LIKELIHOOD

    def fit(self):
        self.m.migrad()
        return self

    def migrad(self):
        self.m.migrad()
        return self

    def minos(self):
        self.m.minos()
        return self

    @property
    def log_likelihood(self):
        return self.log_likelihood_null(*self.values)

    @property
    def c(self):
        return self.m.values["c"]

    @property
    def phi(self):
        return self.m.values["phi"]

    @property
    def values(self):
        return self.m.values


#%%


class Frequentist:
    def __init__(self, data, method="posterior"):
        self.PMD = FrequentistPMD(data, method=method).fit()
        self.null = FrequentistNull(data, method=method).fit()
        p = fit_utils.compute_likelihood_ratio(self.PMD, self.null)
        self.lambda_LR, self.lambda_LR_P, self.lambda_LR_z = p

        self.valid = self.PMD.valid

        self.data = data
        self.x = data["x"]
        self.k = data["k"]
        self.N = data["N"]
        self.method = method

    def __repr__(self):
        s = f"Frequentist(data, method={self.method}). \n\n"
        s += self.__str__()
        return s

    def __str__(self):
        s = f"A = {self.A:.3f}, q = {self.q:.3f}, "
        s += f"c = {self.c:.5f}, phi = {self.phi:.1f} \n"
        s += f"D_max = {self.D_max:.3f} +/- {self.D_max_std:.3f}, "
        s += f"rho_Ac = {self.rho_Ac:.3f} \n"
        s += f"log_likelihood_PMD  = {self.PMD.log_likelihood:.3f} \n"
        s += f"log_likelihood_null = {self.null.log_likelihood:.3f} \n"
        s += (
            f"lambda_LR = {self.lambda_LR:.3f}, "
            f"lambda_LR as prob = {self.lambda_LR_P:.4%}, "
            f"lambda_LR as z = {self.lambda_LR_z:.3f} \n"
        )
        s += f"valid = {self.valid}"
        return s

    @property
    def D_max(self):
        return self.PMD.D_max

    @property
    def D_max_std(self):
        return self.PMD.D_max_std

    @property
    def A(self):
        return self.PMD.A

    @property
    def A_std(self):
        return self.PMD.A_std

    @property
    def q(self):
        return self.PMD.q

    @property
    def q_std(self):
        return self.PMD.q_std

    @property
    def c(self):
        return self.PMD.c

    @property
    def c_std(self):
        return self.PMD.c_std

    @property
    def phi(self):
        return self.PMD.phi

    @property
    def phi_std(self):
        return self.PMD.phi_std

    @property
    def rho_Ac(self):
        return self.PMD.rho_Ac

    @property
    def chi2(self):
        return self.PMD.chi2


#%%


def compute_LR(fit1, fit2):
    return -2 * (fit1.log_likelihood - fit2.log_likelihood)


def compute_LR_All(fit_all):
    return compute_LR(fit_all.PMD, fit_all.null)


def compute_LR_ForRev(fit_forward, fit_reverse):
    LR_forward = compute_LR(fit_forward.PMD, fit_forward.null)
    LR_reverse = compute_LR(fit_reverse.PMD, fit_reverse.null)
    return LR_forward + LR_reverse


def compute_LR_ForRev_All(fit_all, fit_forward, fit_reverse):
    log_lik_ForRev = fit_forward.PMD.log_likelihood + fit_reverse.PMD.log_likelihood
    return -2 * (log_lik_ForRev - fit_all.PMD.log_likelihood)


#%%


def make_fits(fit_result, data):
    np.random.seed(42)

    fit_all = Frequentist(data, method="posterior")

    data_forward = {key: val[data["x"] > 0] for key, val in data.items()}
    data_reverse = {key: val[data["x"] < 0] for key, val in data.items()}

    fit_forward = Frequentist(data_forward, method="posterior")
    fit_reverse = Frequentist(data_reverse, method="posterior")

    vars_to_keep = [
        "lambda_LR",
        "D_max",
        "D_max_std",
        "q",
        "q_std",
        "phi",
        "phi_std",
        "A",
        "A_std",
        "c",
        "c_std",
        "rho_Ac",
        "lambda_LR_P",
        "lambda_LR_z",
        "valid",
    ]

    for var in vars_to_keep:
        fit_result[f"{var}"] = getattr(fit_all, var)

    numerator = fit_forward.D_max - fit_reverse.D_max
    delimiter = np.sqrt(fit_forward.D_max_std ** 2 + fit_reverse.D_max_std ** 2)
    fit_result["asymmetry"] = np.abs(numerator) / delimiter

    for var in vars_to_keep:
        fit_result[f"forward_{var}"] = getattr(fit_forward, var)

    for var in vars_to_keep:
        fit_result[f"reverse_{var}"] = getattr(fit_reverse, var)

    fit_result["LR_All"] = compute_LR_All(fit_all)
    fit_result["LR_ForRev"] = compute_LR_ForRev(fit_forward, fit_reverse)
    fit_result["LR_ForRev_All"] = compute_LR_ForRev_All(
        fit_all, fit_forward, fit_reverse
    )

    fit_result["chi2_all"] = fit_all.chi2
    fit_result["chi2_forward"] = fit_forward.chi2
    fit_result["chi2_reverse"] = fit_reverse.chi2
    fit_result["chi2_ForRev"] = fit_forward.chi2 + fit_reverse.chi2

    return fit_all, fit_forward, fit_reverse
