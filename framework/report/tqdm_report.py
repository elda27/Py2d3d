from ..framework import Framework
from tqdm import tqdm
import numpy as np


class TqdmReport(Framework):
    def __init__(self, interval=1000):
        self.interval = interval

    def setup(self, parent):
        self.logger = tqdm()
        return self.logger

    def generate_post(self, population):
        self.population = population
        return population

    def update_pre(self, metric):
        self.logger.set_description(
            'metric={:06f}'.format(np.mean(metric)), refresh=False
        )
        return metric

    def update_post(self, optimizer):
        if (optimizer.iteration % self.iteration == 0):
            optimizer.print_state(self.logger)
