# Update live API-able data

from regime_identification.Data.yf_tickers import pull_prices, save_prices
import yaml

# Importing the config
config = yaml.safe_load(open("config.yml"))

# ETFs
etf_dir = "../Data/ETFs/"

## Pull from yf
print("Pulling...")
etfs = pull_prices(config["ETFS"], period = config["PERIOD"], save_dir = etf_dir)

## Save
print("Saving...")
save_prices(etfs, save_dir = etf_dir)

