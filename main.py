import numpy as np
import pandas as pd
from pathlib import Path
from metaDMG.utils import load_config, get_results_dir
from metaDMG.fit import run_workflow
from metaDMG_viz import start_dashboard
from metaDMG.filters import load_results, filter_results

from metaDMG.fit import serial, fit_utils, fits


config_path = Path("config.yaml")
config_path = Path("efd40f0223-config.weight-0.yaml")
# config_path = Path("98ec3bda1f-config.weight-1.yaml")
config = load_config(config_path)
configs = fit_utils.make_configs(config)

config = configs[0]

# config["bayesian"] = True
forced = False

x = x

serial.run_LCA(config)
df_mismatches = serial.get_df_mismatches(config)
df_fit_results = serial.get_df_fit_results(config, df_mismatches)
df_results = serial.get_df_results(config, df_mismatches, df_fit_results, forced=False)
read_ids_mapping = serial.get_database_read_ids(config)


for tax_id, group in fits.get_groupby(df_mismatches):
    break

data = fits.group_to_numpyro_data(config, group)



get_results_dir(config_path=None, results_dir=None)
get_results_dir(config_path=Path("efd40f0223-config.weight-0.yaml"), results_dir=None)

get_results_dir(config_path=None, results_dir=Path("./data/results"))
get_results_dir(config_path=Path("config.yaml"), results_dir=Path("./data/results"))
