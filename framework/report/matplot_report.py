from ..framework import Framework
import matplotlib.pyplot as plt


class MatplotReport(Framework):
    def __init__(self, callback, interval=1000):
        self.interval = interval
        self.callback = callback

    def update_post(self, optimizer):
        if (optimizer.iteration % self.interval == 0):
            self.callback()
            plt.show(block=False)
