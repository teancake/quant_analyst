import numpy as np
import pandas as pd
import os

from data.base_data import BaseData

from utils.log_util import get_logger
logger = get_logger()


class StockZhaData(BaseData):

    @classmethod
    def get_estu(cls, df):
        logger.info("get estu")
        df = cls.delete_st_pt(df)
        df = cls.delete_new_listed(df)
        df = cls.delete_insufficient_trade_dates(df)
        return df

    @classmethod
    def market_cap_weighted_avg(cls, df):
        logger.info("market cap weighted average.")
        mv = cls.get_daily_basic()[["total_mv"]]
        temp_df = df.join(mv)
        temp_df = temp_df.groupby("trade_date").apply(
            lambda x: x.mul(x["total_mv"], axis=0).sum() / x["total_mv"].sum())
        logger.info(f"index {temp_df.index}")

        return temp_df[df.columns]

    @classmethod
    def cs_norm(cls, df):
        logger.info("cross-sectional normalisation.")
        mu_df = cls.market_cap_weighted_avg(df)
        sigma_df = df.groupby("trade_date").std()
        logger.info(f"index {sigma_df.index}")

        return (df - mu_df) / sigma_df

    @classmethod
    def standardize(cls, df):
        logger.info("standardize.")
        std_df = cls.cs_norm(df)
        win_df = cls.winsorize(std_df)
        return cls.cs_norm(win_df)

    @classmethod
    def fillna(cls, df):
        logger.info("fillna, regress within each industry, fill with regression result")
        ind = cls.get_sw_industry()[["industry"]]
        mv = cls.get_daily_basic()[["total_mv"]]
        temp_df = df.join(ind).join(mv)
        temp_df.dropna().groupby("industry", group_keys=False).apply(
            lambda x: cls.wls(x, ["total_mv"], x.columns.drop(["industry", "total_mv"])))
        logger.info(f"index {temp_df.index}")

    @classmethod
    def cs_neutralize(cls, df):
        logger.info("cs neutralize, regress at each cross-section with industry and ln cap")

        def get_ols_residual(df, x_cols, y_cols):
            model_dict = cls.wls(df, x_cols, y_cols)
            res = pd.DataFrame()
            # model resid comes with index, so no need to worry about index of res
            for key in model_dict.keys():
                res[key] = model_dict[key].resid
            return res

        temp_df = df
        if "industry" not in df.columns:
            ind = cls.get_sw_industry()[["industry"]]
            temp_df = temp_df.join(ind)
        if "total_mv" not in df.columns:
            mv = cls.get_daily_basic()[["total_mv"]]
            temp_df = temp_df.join(mv)
        temp_df["ln_cap"] = np.log(temp_df["total_mv"])
        temp_df = pd.get_dummies(temp_df, columns=["industry"], drop_first=True, dtype=int)
        x_cols = temp_df.columns[temp_df.columns.str.contains("industry")].tolist()
        x_cols.append("ln_cap")
        print(f"temp_df {temp_df}")
        temp_df.groupby("trade_date").apply(lambda x: get_ols_residual(x, x_cols, df.columns))
        # logger.info(f"index {temp_df.index}")

        return temp_df[df.columns]

    @staticmethod
    def get_stock_info():
        logger.info("get stock info.")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_stock_basic.csv")
        df = pd.read_csv(fname, index_col=["code"], parse_dates=["ipo_date"])
        df = df.rename(columns={"sec_name": "name"})
        df.index.name = "ts_code"
        df = df[["name", "industry", "ipo_date"]]
        return df

    @staticmethod
    def get_index_daily():
        logger.info("get index daily.")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_index_daily.csv")
        df = pd.read_csv(fname, parse_dates=["trade_date"], index_col=["ts_code", "trade_date"])
        return df

    @staticmethod
    def get_daily():
        logger.info("get tushare daily")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_daily.csv")
        df = pd.read_csv(fname, parse_dates=["trade_date"], index_col=["ts_code", "trade_date"])
        df = df.join(StockZhaData.get_adj_factor())
        df["close_adj"] = df["close"] * df["adj_factor"]
        return df

    @staticmethod
    def get_daily_basic():
        logger.info("get tushare daily basic")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_daily_basic.csv")
        df = pd.read_csv(fname, parse_dates=["trade_date"], index_col=["ts_code", "trade_date"])
        df = df.join(StockZhaData.get_adj_factor())
        df["close_adj"] = df["close"] * df["adj_factor"]
        return df

    @staticmethod
    def get_sw_industry():
        logger.info("get sw industry")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_index_member_all.csv")
        df = pd.read_csv(fname, parse_dates=["in_date", "out_date"], index_col=["ts_code"])
        df["industry"] = df["l1_name"]
        return df

    @staticmethod
    def get_adj_factor():
        logger.info("get tushare adj factor")
        fname = os.path.join(os.path.dirname(__file__), "sample/tushare_adj_factor.csv")
        df = pd.read_csv(fname, parse_dates=["trade_date"], index_col=["ts_code", "trade_date"])
        return df[["adj_factor"]]

    @staticmethod
    def get_balancesheet():
        return pd.DataFrame()

    @staticmethod
    def get_cashflow():
        return pd.DataFrame()

    @staticmethod
    def get_income_statement():
        return pd.DataFrame()

    @staticmethod
    def get_trade_calendar():
        return list()



    @staticmethod
    def get_fina_indicator():
        return pd.DataFrame()

    @classmethod
    def delete_st_pt(cls, df):
        temp_df = df.join(cls.get_stock_info())
        logger.info(f"delete st pt company, data size {len(df)}, company {len(temp_df['name'].unique())}")
        temp_df = temp_df[~temp_df["name"].str.contains("ST|PT|退")]
        logger.info(f"delete st pt company done, data size {len(temp_df)}, company {len(temp_df['name'].unique())}")
        return temp_df[df.columns]

    @classmethod
    def delete_new_listed(cls, df):
        temp_df = df.join(cls.get_stock_info())
        logger.info(f"delete new listed company, data size {len(df)}, company {len(temp_df['name'].unique())}")
        temp_df = temp_df[
            (temp_df.index.get_level_values(level="trade_date") - temp_df["ipo_date"]).apply(lambda x: x.days > 365)]
        logger.info(
            f"delete new listed company done, data size {len(temp_df)}, company {len(temp_df['name'].unique())}")
        return temp_df[df.columns]

    @classmethod
    def delete_insufficient_trade_dates(cls, df, n=252):
        logger.info(f"delete company of insufficient trade dates, data size {len(df)}, company {len(df.index.get_level_values('ts_code').unique())}")
        filter_df = (df.groupby("ts_code").size() >= n).to_frame("is_insufficient_trade_dates")
        df = df.join(filter_df)
        df = df[df["is_insufficient_trade_dates"]]
        logger.info(f"delete company of insufficient trade dates done, data size {len(df)}, company {len(df.index.get_level_values('ts_code').unique())}")
        return df