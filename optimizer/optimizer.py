from abc import abstractmethod, ABCMeta


class Optimizer(metaclass=ABCMeta):
    def __init__(self):
        self.frameworks = []
        self.optimizing = True

    def add_framework(self, framework):
        self.frameworks.append(framework)

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
