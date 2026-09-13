# Script to automatically load all cached data into a new notebook

#
# IMPORTING LIBS & CONFIG
#
from regime_identification.Data.yf_tickers import load, load_prices, save_prices
from regime_identification.Features.features import get_log

import pandas as pd
import numpy as np
import yaml
from tqdm import tqdm # Loading bars

# Importing the config
config = yaml.safe_load(open("config.yml"))
windows = config["WINDOWS"]

#
# LOAD SAVED DATA
#
print("Loading data...")

# ETFs
print("ETFs")
etfs = load_prices("../Data/ETFs/", are_in = config["ETFS"])

# Extramarket
print("Extramarket")
exm = load("../Data/Extramarket/extramarket.csv")


#
# END
#

print(f"\nDone!")
