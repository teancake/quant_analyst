import pandas as pd
import lightgbm as lgb

from .base_model import BaseModel
from utils.log_util import get_logger

logger = get_logger()


class ArimaModel(BaseModel):
    # arima模型可以参考Python for Finance Cookbook的Chapter 6 

    def feature_engineering(self) -> (pd.DataFrame, pd.DataFrame):
        pass

    def fit(self) -> (object, pd.DataFrame):
        pass

    def predict(self, x: pd.DataFrame) -> pd.DataFrame:
        pass


class LgbmModel(BaseModel):
    def __init__(self):
        super().__init__()

    def feature_engineering(self):
        logger.info("feature engineering")
        df = StockData().load_data()
        logger.info(f"df sample {df}")
        df["pct_chg"] = df.sort_index(level="date", ascending=True).groupby("ticker")["close"].pct_change().values
        df["ma5"] = df.groupby("ticker")["pct_chg"].rolling(window=5).mean().values
        df["ma5_std"] = df.groupby("ticker")["pct_chg"].rolling(window=5).std().values
        df["ma20"] = df.groupby("ticker")["pct_chg"].rolling(window=5).mean().values
        df["ma20_std"] = df.groupby("ticker")["pct_chg"].rolling(window=5).std().values
        df["label"] = df.groupby("ticker")["pct_chg"].shift(periods=-3)
        df.dropna(inplace=True, subset="label")
        logger.info(f"df sample after feature engineering {df}")
        return df

    def train_test_split(self, df):
        logger.info("split train and test dataset.")
        dates = df.index.get_level_values("date")
        split_date = dates[int(len(df) * 0.95)]
        logger.info(f"min date {dates.min()}, max date {dates.max()}, split date {split_date}")
        df_train = df.loc[dates < split_date]
        df_test = df.loc[dates >= split_date]
        logger.info(f"training set size {len(df_train)}, validation set size {len(df_test)}")
        x_cols = ["amount", "pct_chg", "ma5", "ma5_std", "ma20", "ma20_std"]
        y_cols = ["label"]
        return df_train[x_cols], df_train[y_cols], df_test[x_cols], df_test[y_cols], x_cols

    def get_model_config(self):
        params = {"metric": "mse",
                  "verbosity": -1,
                  "learning_rate": 0.05814374665204413,
                  "max_depth": 12,
                  "lambda_l1": 0.2788050348029096,
                  "lambda_l2": 8.486058444555043e-07,
                  "num_leaves": 10,
                  "feature_fraction": 0.8882445798293603,
                  "bagging_fraction": 0.9529766897517215,
                  "bagging_freq": 4,
                  "min_child_samples": 5,
                  "max_bin": 255,
                  "min_data_in_leaf": 5,
                  "boosting_type": "gbdt",
                  "objective": "regression"
                  }
        return params

    def fit(self):
        config = self.get_model_config()
        x_train, y_train, x_test, y_test, x_cols = self.train_test_split(self.feature_engineering())
        dtrain = lgb.Dataset(x_train, label=y_train, feature_name=x_cols)
        dvalid = lgb.Dataset(x_test, label=y_test, feature_name=x_cols)
        logger.info("start training")
        lgbm = lgb.train(config, dtrain, valid_sets=[dtrain, dvalid])
        logger.info("training done")
        metrics_df = pd.DataFrame(lgbm.best_score)
        logger.info(f"metric {metrics_df}")
        self.model = lgbm
        return lgbm, metrics_df

    def predict(self, x):
        model = self.fit() if self.model is None else self.model
        return model.predict(x)


if __name__ == '__main__':
    model = LgbmModel()
    model.fit()
