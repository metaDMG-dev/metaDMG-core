#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from metaDMG.utils import make_configs
from metaDMG.filters import load_results, filter_results
from metaDMG.fit import serial, fit_utils

#%%
config_path = Path("config.yaml")
# config_path = Path("config_local.yaml")
# config_path = Path("config_forward.yaml")
# config_path = Path("config_all.yaml")
# config_path = Path("config_old.yaml")
# config_path = Path("metaDMG_config.yaml")
# config_path = Path("5cdd545807-config.weight-0.yaml")
# config_path = Path("efd40f0223-config.weight-0.yaml")
# config_path = Path("5922fb11a0-config.weight-0.yaml")
# config_path = Path("errors.yaml")
# config = load_config(config_path)
# configs = fit_utils.make_configs(config)

# config = configs[0]

configs = make_configs(config_path)
config = configs.get_first()
# config = configs.get_nth(0)

# config["cores"] = 1
# config["bayesian"] = True
# config["bayesian"] = False
# config["forward_only"] = False
# config["forward_only"] = True
forced = True
forced = False

#%%

x = x  # type: ignore

#%%

serial.run_thorfinn(config, forced=forced)
df_mismatches = serial.get_df_mismatches(config, forced=forced)
df_fit_results = serial.get_df_fit_results(config, df_mismatches, forced=forced)
df_results = serial.get_df_results(config, df_mismatches, df_fit_results, forced=forced)


results_dir = "./data/results"
config_path = None

df_results = load_results(
    config_path=config_path,
    results_dir=results_dir,
)


#%%

for tax_id, group in serial.fits.get_groupby(df_mismatches):
    if tax_id == 61870:
        break


from metaDMG.fit.fits import group_to_numpyro_data

data = group_to_numpyro_data(config, group)  # type: ignore
sample = config["sample"]

from metaDMG.fit import bayesian

config["bayesian"] = True
mcmc_PMD, mcmc_null = bayesian.init_mcmcs(config)

# bayesian.fit_mcmc(mcmc_PMD, data)
# bayesian.fit_mcmc(mcmc_null, data)
# d_results_PMD = bayesian.get_lppd_and_waic(mcmc_PMD, data)
# d_results_null = bayesian.get_lppd_and_waic(mcmc_null, data)
# z = bayesian.compute_z(d_results_PMD, d_results_null)
