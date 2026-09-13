# Libs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

from tqdm import tqdm # Loading bars

'''
TEST-TRAINING SPLIT
'''
# Need this for some filtering
default_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']


# Only find the split date
## TODO: Make consistent/integrate with splitting function
def find_split(*args, split = 0.8): # List should contain all dfs with respective time series data
    data = list()
    for i in args:
        if type(i) is list:
            # print(f"is list")
            data.extend(i)
        elif type(i) is dict:
            # print(f"is dict")
            data.extend(i.values())
        else:
            # print(f"is other")
            data.append(i)

    # Find overlapping dates
    dates = []
    for i in tqdm(data):
        if not dates:
            dates = set(i.index)
        else: 
            dates = dates & set(i.index)

        # print(f"Overlapping dates: {len(dates)}")

    # Determine split in overlap
    dates = sorted(list(dates)) # Default sorts ascending
    split_point = int(len(dates) * split)
    # print(split_point)
    training_dates = dates[:split_point]
    test_dates = dates[split_point:]
    split_date = dates[split_point]

    return training_dates, test_dates, split_date
        
# Recent data splits (DEPRICATED)
## TODO: Make consistent/integrate with split finder
def concat_split_recent(price_list_nona, split, buffer_months = 0): # Proper version
    df = pd.concat(price_list_nona)
    df = df.dropna(how = "all", axis = 1).dropna(how = "any") # Drop full-empty cols, then drop invalid dates
    n_date = df.index.get_level_values("Date").value_counts() # Number of rows per date
    n_date = n_date.sort_index(ascending = True) # Earliest dates first

    # print(n_date)

    t_date = n_date.sum() # Total indexed rows
    split_point = t_date * split # Number of rows in training
    n_date_cs = n_date.cumsum() # Number of rows in training per cutoff date

    # print(f"total rows: {t_date}; split point: {split_point};")

    split_date = n_date_cs[n_date_cs >= split_point].index.min() # First date where training rows exceed desired split threshold
    split_date = pd.to_datetime(split_date)

    # print(f"split date: {split_date}; cumsum @ split: {n_date_cs[split_date]};")

    mask = df.index.get_level_values("Date") <= split_date
    # training = df.loc[df.index.get_level_values("Date") <= split_date]
    # test = df.loc[df.index.get_level_values("Date") > split_date]
    training = df.loc[mask]
    test = df.loc[~mask] # ~ reverses booleans

    if buffer_months:
        training = training[training.index.get_level_values("Date") <= (split_date - timedelta(days = buffer_months * 30))]

    return training, test

'''
FUTURE SHIFTING
'''
# TODO: Make this its own module thing

# TODO: Hacky. Make this more elegant.
def add_f(df, col, period):
    s = df[col]
    df[f"f_{period}d_{col}"] = s.shift(-period)

# Shift columns into future
def get_future(df, windows):
    cols = df.columns
    f_df = pd.DataFrame()
    all_matches = [] # To find cols not matched. 
    for window in windows:
        pattern = re.compile(f".*_{window}d_.*")
        matched_cols = [col for col in cols if pattern.match(col)]
        all_matches += matched_cols

        f_df[matched_cols] = df[matched_cols].shift(-window)

    leftovers = list(set(cols) - set(all_matches))
    f_df[leftovers] = df[leftovers].shift(-1) # Are most likely single-day, so shift -1.

    return f_df

# Find future cols 
def is_future(string):
    return string.startswith("f_") # All future columns start with f_

# Add future cols to dfs
def add_f_cols(price_list, windows, cols = None):
    # Remove previously added cols, to avoid conflicts
    if cols:
        prev_f = list(filter(is_future, list(price_list.values())[1])) # Assuming all dfs have same cols
        prev = [s[2:] for s in prev_f] # Remove f_

        cols = list(set(cols) - set(prev))
        if not cols: return; # Stop if all columns are overlapping
    
    for i in tqdm(price_list):
        if cols is None: 
            f_df = get_future(price_list[i], windows) # Get full future
        else: 
            f_df = get_future(price_list[i][cols], windows) # Contains only relevant future columns

        f_df.columns = "f_" + f_df.columns # Unique ID

        price_list[i] = price_list[i].merge(f_df, 
                            how = "left", # Preserve all rows
                            left_index = True, right_index = True,
                            suffixes = (None, None))

# Split data into x (inputs) and y (outputs)
def split_future(df, goal_cols):
    cols = df.columns
    if goal_cols is None: goal_cols = cols # If none, then all

    y_cols = ["f_" + c for c in goal_cols]
    x_cols = list(set(cols) 
                  - set(filter(is_future, cols))
                  - set(default_cols))
    
    x = df.loc[:, x_cols]
    y = df.loc[:, y_cols]

    return x, y # Present inputs, future outputs

# DO IT ALL!
def make_train_test(price_list, windows, split = 0.8, goal_cols = None, buffer_months = 6): 
    print(f"Adding future columns")
    add_f_cols(price_list, windows = windows, cols = goal_cols)

    print(f"Splitting into training/testing sets")
    training, test = concat_split_recent(price_list, split = split, buffer_months = buffer_months)

    print("Splitting past from future")
    X_training, y_training = split_future(training, goal_cols = goal_cols)
    X_test, y_test = split_future(test, goal_cols = goal_cols)

    return X_training, y_training, X_test, y_test

