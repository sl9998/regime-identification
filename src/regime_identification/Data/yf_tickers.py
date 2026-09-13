# Libs
import pandas as pd
import numpy as np
import os 
from datetime import datetime, timedelta
import yfinance as yf
from tqdm import tqdm # Loading bars

'''
SAVING & LOADING STOCK PRICES
'''

# Convert to compatible date only datetime
def date_only(df):
    df.index = pd.to_datetime(df.index, utc = True) # Convert to datetime if not done already
    df.index = df.index.tz_localize(None) # Remove timezone info
    df.index = df.index.round('D') # Round to date only

# Pull prices from yf and save
def pull_prices(tickers, period, save_dir = "Data/Tickers"):
    prices = dict()
    for i in tqdm(tickers):
        ticker = yf.Ticker(i)
        price_data = ticker.history(period = period)
        if save_dir:
            price_data.to_csv(save_dir + i + ".csv", index = True)     
            
        date_only(price_data)
        prices[i] = price_data
        
    return(prices)

# Load a single price data file
def load(file):
    price_data = pd.read_csv(file, index_col = 0)
    price_data = price_data.astype(float)
    date_only(price_data)
    return price_data

# Load price data from a directory
def load_prices(save_dir, are_in = None, ext = "csv"):
    prices = dict()
    files = os.listdir(save_dir)

    if are_in is not None:
        are_in = [f"{a}.csv" for a in are_in]
        files = list(set(files) & set(are_in)) 

    for i in tqdm(files):
        if not i.endswith(ext): continue # skip if wrong extension
        # price_data = pd.read_csv(save_dir + i, index_col = "Date")
        # date_only(price_data)
        price_data = load(f"{save_dir}{i}")
        ticker = i.rsplit(".", 1)[0] # Remove .csv for compat
        prices[ticker] = price_data

    return(prices)

# Saving price data
def save_prices(price_list, save_dir = "Resources/Processed_prices/"):
    for i in tqdm(price_list):
        price_data = price_list[i]

        price_data.to_csv(save_dir + i + ".csv", index = True)     

