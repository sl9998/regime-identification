# All the commands and stuff from analysis 1 to be imported

'''
A quick note on terminology:
    - "get" means the function returns manipulated data
    - "add" means the function manipulates data in-place (generally avoided)
'''

# Libs
import pandas as pd
import numpy as np

'''
BASIC METRICS
'''

# log anything
def get_log(series):
    log = np.log(series) 
    logret = log.diff()

    # Account for the datetime index bs
    logret = pd.Series(logret, index = series.index)

    return logret

# standardize
def standardize(df, by = pd.DataFrame()):
    if by.empty:
        by = df

    df = (df - by.mean()) / by.std()

    return df
