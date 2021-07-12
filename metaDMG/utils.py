import numpy as np
import yaml

#%%

def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config
