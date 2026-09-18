# Backtesting engine for evaluating trading strategies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

def backtest_strategies(etfs, strategies, condition_col = "cluster", start_date = None, end_date = None, plot = True, leverage = 1, simulate_rb = False): 
    # Convert to pd compatible datetime
    if start_date is not None: start_date = pd.to_datetime(start_date)
    if end_date is not None: end_date = pd.to_datetime(end_date)

    # Make etfs long format
    all_assets = list(etfs.keys())
    etfs = pd.concat(etfs.values()) # Values to avoid multiindex
    if end_date is not None: etfs = etfs[etfs.index <= end_date]
    if start_date is not None: etfs = etfs[etfs.index >= start_date]
    # print(f"cat etfs df:\n{etfs.head()}\n{etfs.tail()}")
    all_dates = etfs.index[~etfs.index.duplicated(keep = "first")]
    n_clusters = int(pd.unique(etfs[condition_col]).max()) + 1 # This method is robust for getting the largest observed cluster; +1 because 0 start

    # Apply strategies to etfs
    strat_dfs = {}
    for name, df in strategies.items():
        df = df.dropna(how = "all", axis = 0)
        # print(f"{name} strat df:\n{df}")

        # Weight columns to equal 1
        df = df.apply(lambda x: x / sum(np.abs(x.dropna())), axis = 0) # Absolute value, because shorts can be negative!
        # print(f"\"{name}\" strat df:\n{df}")

        # Get returns
        ## TODO: Make this separate reusable function
        returns = pd.DataFrame(0, index = all_dates, columns = df.index) # prefilled dates and cluster labels
        ## TODO: Can likely be optimized through some transform magic
        for cluster in list(df.columns):
            for ticker in list(df.index):
                logret = etfs[(etfs["Ticker"] == ticker) & (etfs[condition_col] == cluster)].loc[:, "f_logret"]
                multiplier = df.loc[ticker, cluster]

                logret_adj = logret.dropna() * multiplier # Multiplier = portfolio weight. Drop NAs to avoid problems
                
                returns[ticker] = returns[ticker].add(logret_adj, fill_value = 0) # Fill_value means unindexed information will just add 0 returns

        returns["total"] = returns.sum(axis = 1) * leverage # Rowwise sum of weighted gains; leverage is just a multiple 

        # Bottom out leveraged portfolios
        if leverage > 1:
            totals = returns["total"].cumsum()
            bottoms = totals[totals <= -1] # -1 = 100% loss = bottomed out
            if not bottoms.empty: 
                first_bottom = bottoms.index[0]
                returns = returns[returns.index <= first_bottom]

        strat_dfs[name] = returns

    # Random buys strat
    if simulate_rb: # rb should be number of random portfolios to simulate
        random_buys = pd.DataFrame()

        for i in range(simulate_rb):
            random_buy_strat = pd.DataFrame(np.random.rand(len(all_assets), n_clusters), # Random weights each cluster, equal chance of + and - 
                                            index = all_assets, columns = list(range(n_clusters))) 
            random_buy_strat = random_buy_strat.apply(lambda x: x / sum(np.abs(x.dropna())), axis = 0) # Equalized to 1 per cluster
            random_buy = pd.DataFrame()

            returns = pd.DataFrame(0, index = all_dates, columns = random_buy_strat.index) # prefilled dates and cluster labels
            # TODO: Replace with universal function
            for cluster in list(random_buy_strat.columns):
                for ticker in list(random_buy_strat.index):
                    logret = etfs[(etfs["Ticker"] == ticker) & (etfs[condition_col] == cluster)].loc[:, "f_logret"]
                    multiplier = random_buy_strat.loc[ticker, cluster]

                    logret_adj = logret.dropna() * multiplier # Multiplier = portfolio weight. Drop NAs to avoid problems
                    
                    returns[ticker] = returns[ticker].add(logret_adj, fill_value = 0) # Fill_value means unindexed information will just add 0 returns

            returns["total"] = returns.sum(axis = 1) * leverage # Rowwise sum of weighted gains; leverage is just a multiple 

            # Bottom out leveraged portfolios
            if leverage > 1:
                totals = returns["total"].cumsum()
                bottoms = totals[totals <= -1] # -1 = 100% loss = bottomed out
                if not bottoms.empty: 
                    first_bottom = bottoms.index[0]
                    returns = returns[returns.index <= first_bottom]

            random_buys[i] = returns["total"]

    # PLOTTING
    if plot == True:
        all_totals = pd.DataFrame()
        for name, df in strat_dfs.items():
            all_totals[name] = df["total"]

        all_totals = all_totals.cumsum()

        if simulate_rb:
            random_buys = random_buys.cumsum()
            # sns.lineplot(random_buys, color = "grey", alpha = 0.2)
            plt.plot(random_buys, color = "grey", alpha = 0.1)
        
        if leverage > 1: 
            plt.axhline(y = -1, color = "red", linestyle = "--") # Bust line for leveraged portfolios

        sns.lineplot(all_totals).set_ylabel("Cumulative log returns")
        plt.show()
        plt.close()

    return strat_dfs
