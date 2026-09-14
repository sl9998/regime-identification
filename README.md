market-forecasting
=======

## Abstract
> Recreational quant research. I am not responsible for financial disasters resulting from using this repo.

## Installation

Clone the repo:
```
git clone https://github.com/sl9998/market-forecasting.git
cd market-forecasting
```

Make a venv:
```
python -m venv .venv
source .venv/bin/activate
```
(make sure to use this kernel in the notebooks)

Install dependencies:
```
python -m pip install -r requirements.txt
python -m pip install -e .
```

---

## Introduction & Purpose

Market macro-economic circumstances are [well-known](https://www.ssga.com/library-content/assets/pdf/global/pc/2025/decoding-market-regimes-with-machine-learning.pdf) to affect equity performance differently accross asset classes. While research conventionally succeeds in identifying these regimes over long historical periods, there is rarely any out-of-sample (OOS) testing to assess model performance on unseen market data. Additionally, these strategies suffer from strong look-ahead bias where the model is able to retroactively classify periods based on their relation to future circumstances. This would not be possible when deploying a "live" model.

This project aims to develop a robust market regime identification algorithm based on historical market and macro-economic data. Forward OOS regime-based statistical tests and trading strategies will then be used to assess the consistency of best and worst performing asset classes in each phase. This necessitates a biphasic approach where a model is first trained on a sample period and then deployed OOS. 

## Materials & Methods

### Data

The python [yfinance](https://pypi.org/project/yfinance/) package is used to fetch historical and live market data from [Yahoo! finance](https://finance.yahoo.com/) (yf). Extra-market data not readily available on yf is gathered from various sources (documented in the SOURCES.md file). Plans to utilize public APIs (like [the BoLS's](https://www.bls.gov/bls/api_features.htm)) to take this model live will be explored post semi-succesful backtest.

### Processing, PCA, clustering, backtesting, ...

Python files and notebooks contain detailed information on their respective methodology. 

### Statistical tests

By statistical testing, we want to identify if (1) **within equities** the return distributions differ **between regimes**, and (2) if **between equities** the return distributions differ **within regimes**. Please note that all statistical testing informative for the eventual testing is performed **only in training data!** We do not want data leakage informing us of the future "winning teams".

Both (1) and (2) are tested via the non-parametric **Kruskal-Wallis *H* test**, as financial returns data is fat-tailed and we cannot assume heteroscedasticity. In the case of a rejected null-hypothesis, a post-hoc comparison is needed to identify which distributions differ. For this, Dunn's test is used.

## Results & Discussion

## Limitations

### Methodological

- Clustering is done via a simple KMeans approach. This has poor(er) performance for identifying odd-shaped or -density clusters which may be present in our data.
- Both the PCA and clustering approach are not adjusted for new information in the OOS test (e.g. the preceding OOS dates are added to the algorithms for each day).
- Novel clusters cannot be identified in real-time using this approach. 

### Practical

- As of yet, no system has been set up to retrieve live macro-economic data from a central database. Real-time implementation of this algorithm is currently out-of-scope.
