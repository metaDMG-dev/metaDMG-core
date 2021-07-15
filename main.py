import numpy as np
import pandas as pd
from metaDMG.utils import load_config
from metaDMG_fit import run_workflow
from metaDMG_viz import start_dashboard
from metaDMG.filters import load_results

config = load_config()

df_results = load_results()

x = x

if __name__ == "__main__":
    run_workflow()
    start_dashboard(debug=True)
