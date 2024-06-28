from abc import ABC, abstractmethod


class BaseData(ABC):
    @abstractmethod
    def load_data(self):
        pass
