import numpy as np
import pandas as pd
from pathlib import Path
from metaDMG.utils import load_config
from metaDMG_fit import run_workflow
from metaDMG_viz import start_dashboard
from metaDMG.filters import load_results, filter_results

config_path = Path("config_weight0.yaml")
config = load_config(config_path)
df_results = load_results(config_path)

filter_results(df_results, "tax_id == 9606 & sample == 'gumpaper_weigth1'")

x = x

if __name__ == "__main__":
    run_workflow()
    start_dashboard(debug=True)
