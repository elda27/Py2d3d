from abc import ABCMeta, abstractmethod


class Metric(metaclass=ABCMeta):
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
