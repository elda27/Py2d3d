import matplotlib.pyplot as plt


class SubplotManager:
    def __init__(self, row, column):
        self.row = row
        self.column = column
        self.index = 1

    def __enter__(self):
        fig = plt.subplot(self.row, self.column, self.index)
        return fig

    def __exit__(self, *args):
        self.next()

    def next(self):
        assert self.row * self.column >= self.index
        self.index += 1
