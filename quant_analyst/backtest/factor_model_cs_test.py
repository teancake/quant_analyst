# -*- coding: utf-8 -*-
"""
Created on Fri May 18 22:10:38 2018

@author: XQZhu
https://github.com/Jensenberg/multi-factor/blob/master/self_libs/factor_test.py
"""


import pandas as pd
import numpy as np
import math
import scipy
import statsmodels.api as sm

from utils.log_util import get_logger

logger = get_logger()

class CrossSectionalTest():

    def __init__(self, test_data, market_return):
        # three columns in test_data, the first is return, the second is factor, third column is optional, circ_mv
        # two levels of index, the name of date must be trade_date
        self.test_data = test_data
        self.market_return = market_return


    def layer_test(self, quantile=10):
        '''
        Parameters
        ==========
        test_data: DataFrame
            包含收益率、因子值
        retn_mk: DataFrame
            市场收益率数据
        quantile: int
            层数
        '''
        logger.info("layer test")
        test_data = self.test_data
        retn_mk = self.market_return
        test_data["layer"] = test_data.groupby("trade_date", group_keys=False).apply(lambda x: pd.qcut(x.iloc[:, 1], quantile, labels=False, duplicates="drop"))
        logger.info(f"index {test_data.index}")
        layer_retn = test_data.groupby(["trade_date", "layer"])["return"].mean()
        logger.info(f"index {layer_retn.index}")

        test_data.drop('layer', axis=1, inplace=True)
        layer_retn = layer_retn.unstack()
        layer_retn['t_b'] = layer_retn.iloc[:, -1] - layer_retn.iloc[:, 0]
        layer_retn = layer_retn.join(retn_mk, how='left').dropna()

        nav = (1 + layer_retn).cumprod()
        # Hold Period Return (HPR)
        hpy = nav.iloc[-1, :] - 1
        # conversion factor depends on the frequency of data
        # 12 if monthly, 252 if daily
        periods_in_a_year = 252
        conv_factor = 252 / len(layer_retn)
        annual = (nav.iloc[-1, :]) ** conv_factor - 1
        sigma = layer_retn.std() * math.sqrt(periods_in_a_year)
        sharpe = (annual - 0.036) / sigma
        max_drdw = nav.apply(self.drawdown)

        rela_retn = layer_retn.sub(layer_retn.iloc[:, -1], axis='index')
        rela_nav = (1 + rela_retn).cumprod()
        rela_annual = (rela_nav.iloc[-1, :]) ** conv_factor - 1
        rela_sigma = rela_retn.std() * math.sqrt(periods_in_a_year)
        rela_retn_IR = rela_annual / rela_sigma
        rela_max_drdw = rela_nav.apply(self.drawdown)

        result = {'hpy': hpy,
                  'annual': annual,
                  'sigma': sigma,
                  'sharpe': sharpe,
                  'max_drdw': max_drdw,
                  'rela_annual': rela_annual,
                  'rela_sigma': rela_sigma,
                  'rela_retn_IR': rela_retn_IR,
                  'rela_max_drdw': rela_max_drdw}
        result = pd.DataFrame(result,
                              columns=['hpy', 'annual', 'sigma', 'sharpe',
                                       'max_drdw', 'rela_annual', 'rela_sigma',
                                       'rela_retn_IR', 'rela_max_drdw'])

        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        for col in nav.columns:
            plt.plot(nav.index, nav[col], label=col)
        plt.legend()


        return result.T, nav, layer_retn

    @staticmethod
    def regress(data):
        '''
        data: DataFrame
            第一列为收益率，
            第二列为因子值，
            第三列为流通市值，可选
            使用个股流通市值的平方根作为权重，此举也有利于消除异方差性，见华泰101因子报告

        计算因子收益率、t值、秩相关系数（IC值）

        '''
        y = data.iloc[:, 0]
        x = data.iloc[:, 1]
        w = np.sqrt(data.iloc[:, 2]) if len(data.columns) > 2 else 1.0
        x = sm.add_constant(x)
        model = sm.WLS(y, x, w).fit()
        alpha, beta = model.params
        tvalue = model.tvalues.iloc[1]
        ic_value = scipy.stats.spearmanr(data.iloc[:,:2])[0]

        # regress does not know it is for cross-section, better to leave index to the outside.
        result = pd.DataFrame({"alpha": [alpha], 'beta': [beta], 'tvalue': [tvalue], 'ic': [ic_value]},
                              columns=["alpha", 'beta', 'tvalue', 'ic'])
        return result


    def btic_reg(self):
        '''
        在截面上回归
        '''
        test_data = self.test_data
        beta_t_ic = test_data.groupby(level="trade_date").apply(self.regress)
        # logger.info(f"index {beta_t_ic.index}")
        beta_t_ic = beta_t_ic.reset_index().set_index('trade_date').loc[:, ["alpha", 'beta', 'tvalue', 'ic']]
        return beta_t_ic

    @staticmethod
    def btic_des(data, factor_name):
        '''
        data: DataFrame
            含有return, tvalue, ic
        factor_name: str
            因子名称，仅用于画图时进行标记，下同
        '''
        premium_result = {'Return Mean': data.beta.mean(),
                          'Return Std': data.beta.std(),
                          'idio return mean': data.alpha.mean(),
                          'Return T-test': scipy.stats.ttest_1samp(data.beta, 0)[0],
                          'P(t > 0)': len(data[data.tvalue > 0]) / len(data),
                          'P(|t| > 2)': len(data[abs(data.tvalue) > 2]) / len(data),
                          '|t| Mean': abs(data.tvalue).mean(),
                          'IC Mean': data.ic.mean(),
                          'IC Std': data.ic.std(),
                          'P(IC > 0)': len(data[data.ic > 0]) / len(data.ic),
                          'P(IC > 0.02)': len(data[data.ic > 0.02]) / len(data.ic),
                          'IC IR': data.ic.mean() / data.ic.std()}
        premium_result = pd.DataFrame(
            premium_result, \
            columns=['Return Mean', 'Return Std', 'Return T-test', 'P(t > 0)',
                     'P(|t| > 2)', '|t| Mean', 'IC Mean', 'IC Std', 'P(IC > 0)',
                     'P(IC > 0.02)', 'IC IR'], index=[factor_name]).T
        return premium_result

    @staticmethod
    def btic_plot(data, factor_name):
        import matplotlib.pyplot as plt
        xz = range(len(data))
        xn = data.index.strftime('%Y-%m')

        plt.figure(figsize=(10, 5))
        beta = data['beta']
        plt.bar(xz, beta, label='Return of ' + factor_name)
        plt.legend()
        plt.xlim(xz[0] - 1, xz[-1] + 1)
        plt.ylim(beta.min() - 0.005, beta.max() + 0.005)
        plt.xticks(xz[0:-1:12], xn[0:-1:12])
        plt.show()

        plt.figure(figsize=(10, 5))
        beta_c = 1 + data['beta'].cumsum()
        plt.plot(xz, beta_c, label='Cumulated Return of ' + factor_name)
        plt.legend()
        plt.xlim(xz[0] - 1, xz[-1] + 1)
        plt.ylim(beta_c.min() - 0.005, beta_c.max() + 0.005)
        plt.xticks(xz[0:-1:12], xn[0:-1:12])
        plt.show()

        plt.figure(figsize=(10, 5))
        low = math.floor(beta.min() * 100)
        up = math.ceil(beta.max() * 100)
        bins = pd.Series(range(low, up + 1)) / 100
        plt.hist(beta, bins=bins, label='Return of ' + factor_name)
        plt.legend()
        plt.xlim(low / 100, up / 100)
        plt.xticks(bins, bins)
        plt.show()

        plt.figure(figsize=(10, 5))
        t = data['tvalue']
        plt.bar(xz, t, label='T Value of Return of ' + factor_name)
        plt.legend()
        plt.xlim(xz[0] - 1, xz[-1] + 1)
        plt.ylim(t.min() - 1, t.max() + 1)
        plt.xticks(xz[0:-1:12], xn[0:-1:12])
        plt.show()

        plt.figure(figsize=(10, 5))
        ic = data['ic']
        plt.bar(xz, ic, label='IC of ' + factor_name)
        plt.legend()
        plt.xlim(xz[0] - 1, xz[-1] + 1)
        plt.ylim(ic.min() - 0.01, ic.max() + 0.01)
        plt.xticks(xz[0:-1:12], xn[0:-1:12])
        plt.show()


    def btic(self, factor_name):
        '''
        Parameters
        ==========
        factor_value: DataFrame
            因子值
        factor_name: str
            因子名称
        retn: DataFrame
            股票收益率

        Returns
        =======
        des: DataFrame
            因子收益率与IC值的评价指标
        btic_m: DataFrame
            每一期的beta，T值，IC值

        返回相应的图表
        '''

        logger.info("btic computation")
        btic_m = self.btic_reg()
        des = self.btic_des(btic_m, factor_name)
        self.btic_plot(btic_m, factor_name)
        return des, btic_m

    @staticmethod
    def drawdown(x):
        '''
        Parametes
        =========
        x: DataFrame
            净值数据
        '''
        drawdown = []
        for t in range(len(x)):
            max_t = x.iloc[:t + 1].max()
            drawdown_t = min(0, (x.iloc[t] - max_t) / max_t)
            drawdown.append(drawdown_t)
        return pd.Series(drawdown).min()

