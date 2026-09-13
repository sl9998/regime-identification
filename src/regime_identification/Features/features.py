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
UTILITIES
'''

# NAs % per column
def missing_pct(df):
    miss = df.isnull().sum() / len(df)
    return(miss)

def standardize(df, by = pd.DataFrame()):
    if by.empty:
        by = df

    df = (df - by.mean()) / by.std()
    return df

# Quickly get names of all windows' columns according to standard format
def colnames(windows, prefix = "Close", suffix = "avgret"):
    colnames = []
    for window in windows:
        colnames.append(f"{prefix}_{window}d_{suffix}")

    return(colnames)
        
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

# log returns
def get_logret(df):
    logret = get_log(df["Close"])

    # Account for the datetime index bs
    logret = pd.Series(logret)
    logret.index = df.index

    return logret

# Average return
def get_avgs(df, window): # Can be df or single series
    roll = df.rolling(window, 
                          min_periods = window, # Necessitate sequential data
                          center = False, # Index is rightmost window value
                         ).mean() 
    return(roll)

# Volatility
def get_volatility(df, window):
    roll = df.rolling(window, 
                          min_periods = window, # Necessitate sequential data
                          center = False, # Index is rightmost window value
                         ).std() 
    return(roll)

# Sigma/outlierness
def get_sigma(ret, avgret, volatility):
    sigma = (ret - avgret) / volatility
    return sigma

# Get all basic metrics
def get_metrics(df, col, windows, calc_acorr = False):
    # Log returns
    logret = get_log(df[col])
    df[f"{col}_logret"] = logret

    for w in range(len(windows)):
        window = windows[w]

        # Rolling stats
        avgret = get_avgs(logret, window) # Beware of the datetime index!
        df[f"{col}_{window}d_avgret"] = avgret

        volatility = get_volatility(logret, window)
        df[f"{col}_{window}d_volatility"] = volatility

        # Autocorrelation
        if calc_acorr == True:
            acorr = get_acorr_cat(logret, window)
            df[f"{col}_{window}d_acorr"] = acorr
        ## Note: Currently unuseable state

        # Sigmas & exclusive momentum
        if w < 1: # For the first rolling window, get sigma vs present day 
            df[f"{col}_1d_sigma"] = get_sigma(logret, avgret, volatility)
            df[f"{col}_{window}d_avgret_excl"] = (avgret * window - logret) / (window - 1)  
        else: # For the rest, get sigma vs previous window
            p_window = windows[w - 1]
            df[f"{col}_{p_window}d_sigma"] = get_sigma(df[f"{col}_{p_window}d_avgret"], avgret, volatility)
            df[f"{col}_{window}d_avgret_excl"] = (avgret * window - df[f"{col}_{p_window}d_avgret"] * p_window) / (window - p_window)  

    return df


'''
CORRELATION
'''
# Normal correlation (e.g. to global tickers)
def get_corr(series, series2, window):
    corr = series.rolling(window, 
                          min_periods = window, 
                          center = False, 
                          ).corrwith(series2)
    return(corr)

# Autocorrelation
def get_acorr(series, window):
    return(get_corr(series, series.shift(1), window))
    
# Categorical autocorrelation
def get_acorr_cat(series, window):
    b = series > 0
    return(get_corr(b, b.shift(1), window))

