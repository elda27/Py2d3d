from abc import ABCMeta, abstractmethod
from metric.cache.provider import Provider


class Metric(metaclass=ABCMeta):
    provider = Provider()

    @abstractmethod
    def calculate(self, *args, **kwargs):
        """ Calculate metric.
        """
        raise NotImplementedError()

    @abstractmethod
    def serialize_config(self):
        """Make dictionary for serialization this class.
        A dictionary can be constructed this class.
        """

        raise NotImplementedError()

    @abstractmethod
    def load_config(self, config):
        """Load configuration in order to construct this class.
        """

        raise NotImplementedError()

    @classmethod
    def provide(cls, image):
        return cls.provider.provide(image)
