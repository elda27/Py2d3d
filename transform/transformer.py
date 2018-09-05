from abc import abstractmethod, ABCMeta
from typing import List


class Transformer(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, model, **params):
        raise NotImplementedError()

    @classmethod
    def parameterize(cls)->List[str]:
        """Declare parameters for transformation.

        Returns:
            List[str]: Declared parameter list.
        """

        return ['pose']  # "pose" is reserved for rigid transformation.
