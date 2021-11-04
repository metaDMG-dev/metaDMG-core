import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from metaDMG.utils import load_config, get_results_dir
from metaDMG.fit import run_workflow
from metaDMG_viz import start_dashboard
from metaDMG.filters import load_results, filter_results

from metaDMG.fit import serial, fit_utils  # , fits

config_path = Path("config.yaml")
config_path = Path("config_vincent.yaml")
# config_path = Path("5cdd545807-config.weight-0.yaml")
# config_path = Path("efd40f0223-config.weight-0.yaml")
# config_path = Path("5922fb11a0-config.weight-0.yaml")
# config_path = Path("errors.yaml")
config = load_config(config_path)
configs = fit_utils.make_configs(config)

config = configs[0]

# config["cores"] = 6
# config["bayesian"] = True
# config["bayesian"] = False
forced = True
forced = False

serial.run_LCA(config, forced=forced)
df_mismatches = serial.get_df_mismatches(config, forced=forced)
df_fit_results = serial.get_df_fit_results(config, df_mismatches, forced=forced)
df_results = serial.get_df_results(config, df_mismatches, df_fit_results, forced=forced)

# for tax_id, group in serial.fits.get_groupby(df_mismatches):
#     if tax_id == 61870:
#         break

#%%
