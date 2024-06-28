from abc import ABC, abstractmethod
import pandas as pd


class BaseModel(ABC):

    @abstractmethod
    def fit(self) -> (object, pd.DataFrame):
        pass

    @abstractmethod
    def predict(self, x: pd.DataFrame) -> pd.DataFrame:
        pass
