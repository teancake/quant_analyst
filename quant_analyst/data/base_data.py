from abc import ABC, abstractmethod
import statsmodels.api as sm

from utils.log_util import get_logger
logger = get_logger()

class BaseData(ABC):

    @staticmethod
    def winsorize(df, lp=0.05, up=0.95):
        logger.info(f"winsorize with lower percentile {lp}, upper {up}")
        return df.clip(lower=df.quantile(lp), upper=df.quantile(up), axis=1)

    @staticmethod
    def wls(df, x_cols, y_cols, weights=1.0):
        res = {}
        for col in y_cols:
            x = sm.add_constant(df[x_cols])
            model = sm.WLS(df[col], x, weights).fit()
            res[col] = model
        return res


