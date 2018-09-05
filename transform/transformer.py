from abc import abstractmethod, ABCMeta
from typing import List


class Transformer(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, model, x, **params):
        raise NotImplementedError()
