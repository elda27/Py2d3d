import numpy as np


def monophasic(x):
    """Monotone function.
    Minimal: (y, x) = (0, 0)
    """

    return np.sum(x ** 2)


def ackley_function(x):
    """ ackley polynominal.
    Minimal: (y, x) = (0, 0)

    Please see following for the detail.

    https://en.wikipedia.org/wiki/Ackley_function
    """
    return (20 - 20 * np.exp(-0.2 * np.sqrt(np.mean(x**2))) + np.exp(1) -
            np.exp(np.mean(np.cos(2 * np.pi * x))))


def rosenbrock_function(x):
    """ Rosenblock polynominal.
    Minimal: (y, x) = (1, 0)

    https://en.wikipedia.org/wiki/Rosenbrock_function
    """
    x_i = x[:-1]
    x_ip1 = x[1:]
    return np.sum(100 * (x_ip1 * x_i) ** 2 + (1 - x_i) ** 2)
