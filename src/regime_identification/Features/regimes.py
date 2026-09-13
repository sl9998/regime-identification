# All commands etc needed for regime identification specifically
'''
TODO: Add import appropriate other modules 
'''
from regime_identification.Features.features import standardize
from regime_identification.Data.yf_tickers import date_only

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sklearn as skl
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from tqdm import tqdm
import yfinance as yf

import matplotlib.pyplot as plt
import seaborn as sns

# Rolling corr matrix
def get_corrM_roll(df, window): 
    df = df.dropna(how = "any")
    m = df.rolling(window = window).corr()

    return m

# Compress stacked matrices into long format
def get_long_corrM(corrM):
    dates = corrM.groupby(level = 0).size().index 

    long_corr = pd.DataFrame()

    for i in tqdm(dates):
        corr = corrM.loc[i] 
        mask = np.triu(np.ones(corr.shape), k=1).astype(bool) # Upper triangle mask
        flat = (
                corr.where(mask) # Only upper (= relevant) triangle
                .stack() 
                .reset_index() 
                ).dropna(how = "any") # Removes lower triangle & diag

        if long_corr.empty: # First observation only adds colnames + first date
            flat.columns = ["var1", "var2", i]
            long_corr = flat
        else:
            corr_col = flat.iloc[:, 2] # Only the corr (assume globs are same order every time)
            long_corr[i] = corr_col # Add column of next date

    # Transform from wide to long 
    long_corr.index = long_corr["var1"] + "_" + long_corr["var2"]
    long_corr = long_corr.T.iloc[2:-1, :]

    return long_corr

# Expanding window normalization
def expanding_norm(df, norm_start):
    norm_start = pd.to_datetime(norm_start)
    df = df.sort_index()
    training = df[df.index < norm_start]
    training = (training - training.mean()) / training.std()

    # Start expanding normalization from the end of training
    m = df.expanding().mean()
    s = df.expanding().std()
    test = (df - m) / s 
    test = test[test.index >= norm_start]
    
    df_out = pd.concat([training, test])

    return(df_out)

def get_pca(df, n_components = None): 
    pca_f = skl.decomposition.PCA(n_components = n_components)
    pca = pca_f.fit(df)
    reduced = pd.DataFrame(pca.transform(df), index = df.index)
    reduced.columns = [f"PC{i}" for i in reduced.columns]

    return pca, reduced

# Scree plot
def scree_pca(pca):
    var_exp = pca.explained_variance_
    scree_y = pca.explained_variance_ / np.sum(pca.explained_variance_)
    scree_x = range(1, len(pca.explained_variance_) + 1)

    fig, ax = plt.subplots(2, 1, sharex = True)

    sns.scatterplot(
                x = scree_x, y = scree_y,
                ax = ax[0]
                ).set_title("Relative")

    sns.scatterplot(
                x = scree_x, y = var_exp,
                ax = ax[1]
               ).set_title("Absolute")
    plt.show()
    plt.close()

''' 
ENSEMBLE COMMANDS
(DO IT ALL!)
'''
def get_corrM(df, corr_window = 21):
    glob_corrM = get_corrM_roll(df, corr_window)
    glob_corr_long = get_long_corrM(glob_corrM)
    # Add to df
    glob_corr_long.columns = glob_corr_long.columns + f"_corr"

    return glob_corr_long

def get_regimes(glob_full, split_date = None,
                do_pca = True, n_pcs = 5, 
                n_clusters = 3, rand = 42,
                show_plots = True,
                zoom = False, t_min = (2019, 1, 1), t_max = (2022, 1, 1)):

    if split_date:
        training = glob_full[glob_full.index < split_date]
    else:
        training = glob_full

    # Standardize data to only known values
    glob_full = standardize(glob_full, by = training).astype(float).dropna(how = "any") # Only standardize to known values
    training = standardize(training).astype(float).dropna(how = "any") 
    # TODO: Expanding standardization!
    
    # Do PCA
    if do_pca:
        pca, training_pcs = get_pca(training, n_components = n_pcs)
        '''
        sns.pairplot(training_pcs) # Only plot training PCs
        plt.show()
        plt.close()
        '''

        full_pcs = pd.DataFrame(pca.transform(glob_full), 
                                index = glob_full.index)
        full_pcs.columns = [f"PC{i}" for i in full_pcs.columns]
    
        # Residualizing
        pred = pca.inverse_transform(full_pcs)
        residuals = glob_full - pred

        training = training_pcs.join(residuals) # Join removes irrelevants 
        glob_full = full_pcs.join(residuals)

    # Clustering
    km = MiniBatchKMeans(n_clusters = n_clusters, random_state = rand)
    km = km.fit(training)

    clusters = pd.DataFrame(km.predict(glob_full), index = glob_full.index) 

    # Add to data
    glob_full["cluster"] = clusters

    '''
    # NOTE: Works but poor results

    gm = GaussianMixture(n_components = n_clusters,
                         covariance_type = "full") 
    gm = gm.fit(training)
    clusters = pd.DataFrame(gm.predict(glob_full), index = glob_full.index) 

    # Add to data
    glob_full["cluster"] = clusters
    '''

    '''
    # NOTE: Agglomerative clustering does NOT allow fitting oos, 
    # so we need a different algorithm even though this was pretty good...

    glob_full = training
    agg = AgglomerativeClustering(n_clusters = n_clusters)
    agg = agg.fit(glob_full)

    glob_full["cluster"] = pd.DataFrame(agg.labels_, index = glob_full.index, columns = ["cluster"])
    '''

    # Plotting
    if show_plots:
        '''
        ## Save time not pairplotting
        sns.pairplot(glob_full)
        plt.show()
        plt.close()
        '''

        ## SPY
        # SPY = pd.read_csv("Resources/Global_prices/SPY.csv", index_col = "Date")
        SPY = yf.Ticker("SPY").history(period = "50y") # Just pull it live, whatever
        date_only(SPY)
        SPY["log(Close)"] = np.log(SPY["Close"]) # / exm["inflation_cpi"] # Adjusted for inflation (lol)

        ''' TODO:
        if zoom:
            for i in [t_min, t_max]:
                i = pd.to_datetime(date(i))
            SPY = SPY[(SPY.index > t_min) & (SPY.index < t_max)] # Zoom in
        '''
        
        test = (SPY
            # [(SPY.index > t_min) & (SPY.index < t_max)] # Zoom in
            .join(glob_full["cluster"])
            .dropna(how = "any")
               )
        sns.lineplot(data = test, x = "Date", y = "log(Close)")
        sns.scatterplot(data = test, x = "Date", y = "log(Close)", 
                        hue = "cluster",
                        s = 30, edgecolor = None)
        plt.show()
        plt.close()

    return glob_full

def plot_clusters(clusters, ticker = "SPY"):
    clusters.name = "cluster" 
    clusters.columns = ["cluster"]

    SPY = yf.Ticker(ticker).history(period = "50y") # Just pull it live, whatever
    date_only(SPY)
    SPY["log(Close)"] = np.log(SPY["Close"]) # / exm["inflation_cpi"] # Adjusted for inflation (lol)

    test = SPY.join(clusters).dropna(how = "any")

    sns.lineplot(data = test, x = "Date", y = "log(Close)") # To account for exponential growth of returns
    sns.scatterplot(data = test, x = "Date", y = "log(Close)", 
                    hue = "cluster",
                    s = 30, edgecolor = None)
    plt.show()
    plt.close()

