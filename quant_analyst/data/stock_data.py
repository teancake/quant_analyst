import pandas as pd

from base_data import BaseData


class StockData(BaseData):
    def load_data(self):
        df = pd.read_csv("stock_data.csv", index_col=['date', 'ticker'])
        return df
