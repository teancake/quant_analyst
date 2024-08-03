import numpy as np
import pandas as pd
from tqdm import tqdm

from data.stock_zha_data import StockZhaData

from utils.log_util import get_logger
logger = get_logger()


class MyAlphaData(StockZhaData):
    @classmethod
    def get_my_alpha_data(cls):
        df = cls.get_daily()
        df = cls.get_estu(df)
        return df.groupby("ts_code", group_keys=False).apply(lambda x: cls._compute_ta_indicator(x))

    @classmethod
    def _compute_ta_indicator(cls, df):
        import MyTT as tt

        df = df.sort_index(level="trade_date")
        open_ = df["open"] * df["adj_factor"]
        high = df["high"] * df["adj_factor"]
        low = df["low"] * df["adj_factor"]
        close = df["close"] * df["adj_factor"]

        ti_map = {}
        ti_map["boll_upper_20"], ti_map["boll_mid_20"], ti_map["boll_lower_20"] = tt.BOLL(close, N=20, P=2)
        ti_map["rsi_6"] = tt.RSI(close, N=6)
        ti_map["rsi_12"] = tt.RSI(close, N=12)
        ti_map["rsi_24"] = tt.RSI(close, N=24)
        ti_map["macd_dif"], ti_map["macd_dea"], ti_map["macd"] = tt.MACD(close, SHORT=12, LONG=26, M=9)
        ti_map["dmi_pdi"], ti_map["dmi_mdi"], ti_map["dmi_adx"], ti_map["dmi_adxr"] = tt.DMI(close, high, low, M1=14, M2=6)
        res = pd.DataFrame(ti_map, index=df.index)
        return res


class Alpha191Data(StockZhaData):
    @classmethod
    def get_alpha191_data(cls):
        df = cls._get_alpha191_input()
        return cls._compute_alpha191_data(df)

    @classmethod
    def _compute_dtm_dbm(cls, OPEN, HIGH, LOW):
        from ta_cn.imports.gtja_long import DELAY, MAX, IF
        dtm = IF(OPEN <= DELAY(OPEN, 1), 0, MAX((HIGH - OPEN), (OPEN - DELAY(OPEN, 1))))
        dbm = IF(OPEN >= DELAY(OPEN, 1), 0, MAX((OPEN - LOW), (OPEN - DELAY(OPEN, 1))))
        return dtm, dbm

    @classmethod
    def _get_alpha191_input(cls):
        daily_df = cls.get_daily()
        daily_df = cls.get_estu(daily_df)

        index_df = cls.get_index_daily()
        bm_df = index_df[index_df.index.get_level_values("ts_code") == "000300.SH"][["open", "close"]].rename(
            columns={"open": "bm_open", "close": "bm_close"}).droplevel("ts_code")
        df = daily_df.join(bm_df)
        df.index.names = ["asset", "date"]

        df["open"] = df["open"] * df["adj_factor"]
        df["high"] = df["high"] * df["adj_factor"]
        df["low"] = df["low"] * df["adj_factor"]
        df["close"] = df["close"] * df["adj_factor"]

        df["volume"] = df["vol"]
        df["vwap"] = df["amount"] * 1000 / df["volume"] / 100
        df["returns"] = df["pct_chg"]
        df["dtm"], df["dbm"] = cls._compute_dtm_dbm(df["open"], df["high"], df["low"])

        df = df.rename(columns={"open": "OPEN",
                                "high": "HIGH",
                                "low": "LOW",
                                "close": "CLOSE",
                                "vwap": "VWAP",
                                "volume": "VOLUME",
                                "amount": "AMOUNT",
                                "returns": "RET",
                                "dtm": "DTM",
                                "dbm": "DBM",
                                "bm_open": "BANCHMARKINDEXOPEN",
                                "bm_close": "BANCHMARKINDEXCLOSE",
                                })
        return df

    @classmethod
    def _compute_alpha191_data(cls, input_df):

        import os
        os.environ['TA_CN_MODE'] = 'LONG'
        import ta_cn.alphas.alpha191 as alpha191

        input_dict = input_df.to_dict(orient='series')
        alpha_list = []
        for i in tqdm(range(1, 191 + 1)):
            name = f"alpha_{i:03d}"
            if i in (165, 183, 30):
                logger.warning(f"skipping {name}")
                continue
            fl = getattr(alpha191, name, None)
            temp = fl(**input_dict)

            alpha_list.append(temp.to_frame(name))
        return pd.concat(alpha_list, axis=1)



class Alpha101Data(StockZhaData):

    @classmethod
    def get_alpha101_data(cls):
        df = cls._get_alpha101_input()
        return cls._compute_alpha101_data(df)

    @classmethod
    def _get_alpha101_input(cls):
        from ta_cn.imports.long_ta import ATR, SMA

        df = cls.get_daily()
        df = cls.get_estu(df)

        df.index.names = ["asset", "date"]

        df["open"] = df["open"] * df["adj_factor"]
        df["high"] = df["high"] * df["adj_factor"]
        df["low"] = df["low"] * df["adj_factor"]
        df["close"] = df["close"] * df["adj_factor"]

        df["returns"] = df["pct_chg"]
        df["volume"] = df["vol"]
        df["vwap"] = df["amount"] * 1000 / df["volume"] / 100
        df["adv5"] = SMA(df["volume"], 5)
        df["adv20"] = SMA(df["volume"], 20)

        return df

    @classmethod
    def _compute_alpha101_data(cls, input_df):
        import os
        os.environ['TA_CN_MODE'] = 'LONG'
        import ta_cn.alphas.alpha101 as alpha101

        input_dict = input_df.to_dict(orient='series')
        alpha_list = []
        for i in tqdm(range(1, 101 + 1)):
            name = f'alpha_{i:03d}'
            if i > 45:
                logger.warning(f"skipping {name}")
                continue
            fl = getattr(alpha101, name, None)
            temp = fl(**input_dict)

            alpha_list.append(temp.to_frame(name))
        return pd.concat(alpha_list, axis=1)

