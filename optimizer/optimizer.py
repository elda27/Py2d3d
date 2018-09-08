from abc import abstractmethod, ABCMeta
from typing import Callable

import numpy as np
from contextlib import contextmanager, ExitStack


class Optimizer(metaclass=ABCMeta):
    def __init__(self):
        self.minimal = None
        self.frameworks = []
        self.optimizing = True
        self.iteration = 0

    def add_framework(self, framework):
        self.frameworks.append(framework)

    def set_initial_guess(self, x0: np.ndarray):
        self.initial_guess = np.asarray(x0)

    def set_deserialization(self, deserializer: Callable[[list], dict]):
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

    @contextmanager
    def setup(self):
        """ Setup optimization and frameworks.
            Derrived classes should override setup_core method
            instead of this method.
        """
        self.setup_core()
        with ExitStack() as stack:
            for framework in self.frameworks:
                stack.enter_context(framework.setup(self))
            yield

    def generate(self):
        while self.optimizing:
            workers = \
                [framework.generate(self) for framework in self.frameworks]
            # Execute pre-process
            for worker in workers:
                next(worker)

            # Generate population
            self.population = self.generate_core()
            self.iteration = self.iteration + 1

            # Execute post-process
            for worker in workers:
                # Send population
                self.population = worker.send(self.population)

            yield self.population

    def update(self, metric):
        workers = [framework.update(metric) for framework in self.frameworks]
        # Execute pre-process
        for worker in workers:
            next(worker)

        # Generate population
        self.metric = metric
        self.update_core(metric)

        # Execute post-process
        for worker in workers:
            # Send population
            worker.send(self)

    def setup_core(self):
        pass

    def print_state(self, stream):
        i = np.argmax(self.metric)
        stream.write('iter:{:08d}, bx:{}, by:{}'.format(
            self.iteration,
            self.population[i], self.metric[i],
        ))

    @abstractmethod
    def generate_core(self):
        raise NotImplementedError()

    @abstractmethod
    def update_core(self, metrics):
        raise NotImplementedError()
