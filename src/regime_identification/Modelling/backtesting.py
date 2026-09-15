# Backtesting engine for evaluating trading strategies

import pandas as pd
import numpy as np
import seaborn as sns

#
# REGIME-BASED STRATEGIES
#
'''
The "strategy" is a df where each column is a condition (here: regime) and each row an asset.
Location [asset, condition] represents how much of an asset to buy in that condition.
Values indicate the ratio of the portfolio to allocate to the asset. 
Ratios are adjusted to total 1 per condition.
'''

def backtest_strategies(etfs, strategies, condition_col = "cluster", start_date = None, end_date = None, plot = True): 
    # Convert to pd compatible datetime
    if start_date is not None: start_date = pd.to_datetime(start_date)
    if end_date is not None: end_date = pd.to_datetime(end_date)

    # Make etfs long format
    etfs = pd.concat(etfs.values()) # Values to avoid multiindex
    if end_date is not None: etfs = etfs[etfs.index <= end_date]
    if start_date is not None: etfs = etfs[etfs.index >= start_date]
    # print(f"cat etfs df:\n{etfs.head()}\n{etfs.tail()}")

    # Apply strategies to etfs
    strat_dfs = {}
    for name, df in strategies.items():
        df = df.dropna(how = "all", axis = 0)
        # print(f"{name} strat df:\n{df}")

        # Equalize columns to 1
        df = df.apply(lambda x: x / sum(np.abs(x.dropna())), axis = 0) # Absolute value, because shorts can be negative!
        # print(f"\"{name}\" strat df:\n{df}")

        # Get returns
        all_dates = etfs.index[~etfs.index.duplicated(keep = "first")]
        returns = pd.DataFrame(0, index = all_dates, columns = df.index) # etfs[~etfs.index.duplicated(keep = "first")].loc[condition_col] # prefilled dates and cluster labels
        ## TODO: Can likely be optimized through some transform magic
        for cluster in list(df.columns):
            for ticker in list(df.index):
                logret = etfs[(etfs["Ticker"] == ticker) & (etfs[condition_col] == cluster)].loc[:, "f_logret"]
                multiplier = df.loc[ticker, cluster]

                logret_adj = logret.dropna() * multiplier # Drop NAs to avoid problems
                
                returns[ticker] = returns[ticker].add(logret_adj, fill_value = 0) # Fill_value means unindexed information will just add 0

        returns["total"] = returns.sum(axis = 1) # Rowwise sum of gains. 

        strat_dfs[name] = returns

    # PLOTTING
    if plot == True:
        all_totals = pd.DataFrame()
        for name, df in strat_dfs.items():
            all_totals[name] = df["total"]

        all_totals = all_totals.dropna(how = "any").cumsum()

        sns.lineplot(all_totals)

    return strat_dfs
