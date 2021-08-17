import numpy as np
import pandas as pd
from pathlib import Path
from metaDMG.utils import load_config
from metaDMG_fit import run_workflow
from metaDMG_viz import start_dashboard
from metaDMG.filters import load_results

config_path = Path("config_weight0.yaml")
config = load_config(config_path)
df_results = load_results(config_path)

x = x

if __name__ == "__main__":
    run_workflow()
    start_dashboard(debug=True)
