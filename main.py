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
# config_path = Path("efd40f0223-config.weight-0.yaml")
# config_path = Path("5922fb11a0-config.weight-0.yaml")
# config_path = Path("errors.yaml")
config = load_config(config_path)
configs = fit_utils.make_configs(config)


config = configs[0]

# config["cores"] = 6
# config["bayesian"] = True
# config["bayesian"] = False
forced = False

x = x

serial.run_LCA(config)
df_mismatches = serial.get_df_mismatches(config)
df_fit_results = serial.get_df_fit_results(config, df_mismatches)
df_results = serial.get_df_results(config, df_mismatches, df_fit_results, forced=False)
read_ids_mapping = serial.get_database_read_ids(config)


for tax_id, group in serial.fits.get_groupby(df_mismatches):
    pass
    break
    if tax_id == 349:
        break

# data = fits.group_to_numpyro_data(config, group)


# import pandas as pd
# from metaDMG_viz.results import wide_to_long_df

# # load a specific sample
# df = pd.read_parquet("./data/results/subs.results.parquet")
# # or all samples
# df = pd.read_parquet("./data/results/")

# # specify a tax_id and a specific sample (in case all samples were loaded)
# tax_id = 1
# sample = "subs"

# # get the specific group
# query = f"sample == '{sample}' & tax_id == {tax_id}"
# group_wide = df.query(query)

# # transform the group from a wide to a long dataframe
# group_long = wide_to_long_df(group_wide)

#%%
