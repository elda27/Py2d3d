from abc import abstractmethod, ABCMeta
from typing import Callable

import numpy as np


class Optimizer(metaclass=ABCMeta):
    def __init__(self):
        self.minimal = None
        self.frameworks = []
        self.optimizing = True

    def add_framework(self, framework):
        self.frameworks.append(framework)

    def set_initial_guess(self, x0: np.ndarray):
        self.initial_guess = x0

    def set_deserialization(self, deserializer: Callable[list]):
        """Set deserializer in order to restore the structure
        of optimizing variable.

        Args:
            deserializer (Callable[list]): A callable object 
                in order to deserialize list to dictionary format.
        """

        self.deserializer = deserializer

    def get_minimal(self)->np.ndarray:
        return self.minimal

    def get_deserialized_minimal(self)->dict:
        if hasattr(self, 'deserializer'):
            return self.deserializer(self.minimal)
        return {'param': self.minimal}

    def setup(self):
        # Do nothing on base class
        pass

    def generate(self):
        while self.optimizing:
            workers = \
                [framework.generate(self) for framework in self.frameworks]
            # Execute pre-process
            for worker in workers:
                next(worker)

            # Generate population
            population = self.generate_core()

            # Execute post-process
            for worker in workers:
                # Send population
                population = worker.send(population)

            yield population

    def update(self, metric):
        workers = [framework.update(metric) for framework in self.frameworks]
        # Execute pre-process
        for worker in workers:
            next(worker)

        # Generate population
        self.update_core(metric)

        # Execute post-process
        for worker in workers:
            # Send population
            worker.send(self)

    @abstractmethod
    def generate_core(self):
        raise NotImplementedError()

    @abstractmethod
    def update_core(self, metrics):
        raise NotImplementedError()
