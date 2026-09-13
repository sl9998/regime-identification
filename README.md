market-forecasting
=======

> Recreational quant research. I am not responsible for financial disasters resulting from using this repo.

#### Installation

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

## Abstract

---

## Introduction & Purpose

Market macro-economic circumstances are [well-known](https://www.ssga.com/library-content/assets/pdf/global/pc/2025/decoding-market-regimes-with-machine-learning.pdf) to affect equity performance differently accross asset classes. While research conventionally succeeds in identifying these regimes over long historical periods, there is rarely any out-of-sample (OOS) testing to assess model performance on unseen market data. Additionally, these strategies suffer from strong look-ahead bias where the model is able to retroactively classify periods based on their relation to future circumstances. This would not be possible when deploying a "live" model.

This project aims to develop a robust market regime identification algorithm based on historical market and macro-economic data. Forward OOS regime-based statistical tests and trading strategies will then be used to assess the consistency of best and worst performing asset classes in each phase. This necessitates a biphasic approach where a model is first trained on a sample period and then deployed OOS where it dynamically adapts to new market conditions. 

## Materials & Methods

The python [yfinance](https://pypi.org/project/yfinance/) package is used to fetch historical and live market data from [Yahoo! finance](https://finance.yahoo.com/) (yf). Extra-market data not readily available on yf is gathered from various sources (documented in the SOURCES.md file). Plans to utilize public APIs (like [the BoLS's](https://www.bls.gov/bls/api_features.htm)) to make this model truly live are in the works.

## Results & Discussion

## Limitations

### Methodological

### Practical

As of yet, no system has been set up to retrieve macro-economic data from a central database "live". Real-time implementation of this algorithm is currently out-of-scope.
