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
    pca_f = skl.decomposition.PCA(n_components = n_components, random_state = 42)
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
PLOTTING
'''

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

