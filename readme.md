## quant_analyst: A Python Framework for Financial Modeling and Analysis
This project aims to streamline the process of modeling and analyzing various financial products. The purpose is to build bridges among existing packages and perform automated analysis. It follows a similar structure as Qlib, but simplified for the time being.

### Structure
This project consists of data collector, data, model, and supporting modules. 
#### data collector
This module focuses on acquiring data from various sources, and normalize the data into a uniform format. Currently, only the US market is considered. yfinance is used, which provides data across products like stocks, funds, futures, bonds, crypto, etc. 

#### data
This module performs data loading, pre-processing, and adapts to time series models.
#### model
This is a model zoo, consisting of models for various financial products. 
#### backtesting
This module uses backtrader to test portfolios constructed from the models. 
