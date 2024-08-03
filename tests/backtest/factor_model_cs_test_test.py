import unittest
import alphalens

import pandas as pd

import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
print(parent_dir)
sys.path.append(os.path.join(parent_dir,"quant_analyst"))

from data.stock_zha_data import StockZhaData
from backtest.factor_model_cs_test import CrossSectionalTest

from data.alpha_data import MyAlphaData



class FactorModelCsTestTest(unittest.TestCase):
    def test_abc(self):
        data = AlphaData()
        daily_df = data.get_daily()
        basic_df = data.get_daily_basic()
        info_df = data.get_stock_info()
        ind = data.get_sw_industry()[["industry"]]
        index_df = data.get_index_daily()

        ta_df = data.get_ta_data(daily_df)

        factor_name = "rsi_6"

        test_data = ta_df[[factor_name]]
        test_data = data.get_estu(test_data)
        test_data = data.standardize(test_data)
        test_data = test_data.dropna()
        test_data = data.cs_neutralize(test_data)

        period = 10
        ret = daily_df.groupby("ts_code", group_keys=False).apply(lambda x: x.sort_index(level="trade_date")["close_adj"].pct_change(periods=period).shift(-period))
        ret = ret.to_frame("return")
        test_data = ret.join(test_data[[factor_name]]).join(basic_df[["circ_mv"]])
        test_data = test_data.dropna()

        index_df = data.get_index_daily()
        # 市场收益不需要复权
        market_return = index_df[index_df.index.get_level_values(level="ts_code") == "000300.SH"][["pct_chg"]] / 100
        market_return = market_return.rename(columns={"pct_chg": "market_return"}).droplevel("ts_code")
        print(f"test data {test_data}, market return {market_return}")
        test = CrossSectionalTest(test_data, market_return)
        result, nav, layer_retn = test.layer_test(quantile=5)
        print(f"layer test result {result}, nav {nav}, layer return {layer_retn}")

        des, btic_m = test.btic(factor_name=factor_name)
        print(f"des {des}, btic_m {btic_m}")

        # alphalens
        al_data = test_data
        # 价格做后复权
        price = daily_df[["close_adj"]]
        al_data = al_data.join(price).join(ind).dropna()
        al_data = al_data.swaplevel(0, 1)
        ticker_sector = al_data.droplevel("trade_date")["industry"].to_dict()
        sector_names = {}
        for elem in set(ticker_sector.values()):
            sector_names[elem] = elem
        print(f"al_data {al_data}")
        factor_data = alphalens.utils.get_clean_factor_and_forward_returns(al_data[factor_name],
                                                                           al_data["close_adj"].unstack(),
                                                                           quantiles=5,
                                                                           bins=None,
                                                                           groupby=ticker_sector,
                                                                           groupby_labels=sector_names
                                                                           )
        print(f"factor_data {factor_data}")

        alphalens.tears.create_full_tear_sheet(factor_data)


if __name__ == '__main__':
    unittest.main()