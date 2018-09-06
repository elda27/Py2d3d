import pytest
import optimizer
import numpy as np


def monophasic(x):
    return np.sum(x ** 2)


def ackley_function(x):
    """ ackley polynominal.
    Minimal: (y, x)=(0, 0)

    Please see following for the detail.

    https://en.wikipedia.org/wiki/Ackley_function
    """
    return (20 - 20 * np.exp(-0.2 * np.sqrt(np.mean(x**2))) + np.exp(1) -
            np.exp(np.mean(np.cos(2 * np.pi * x))))


def rosenbrock_function(x):
    """ Rosenblock polynominal.
    Minimal: (y, x) = (0, 1)

    https://en.wikipedia.org/wiki/Rosenbrock_function
    """
    x_i = x[:-1]
    x_ip1 = x[1:]
    return np.sum(100 * (x_ip1 * x_i) ** 2 + (1 - x_i) ** 2)


@pytest.mark.parametrize('function, x, y, options', [
    (monophasic, [0] * 4, 0, {'sigma': 1.0}),
    (ackley_function, [0] * 4, 0, {'sigma': 1.0}),
    (rosenbrock_function, [0] * 4, 1.0, {'sigma': 1.0})
])
def test_cma_es(function, x, y, options):
    x = np.asarray(x)

    opt = optimizer.CmaEsOptimizer()

    x0 = np.random.random(x.shape)
    opt.set_initial_guess(x0)
    opt.set_hyper_parameters(**options)
    opt.setup()
    for population in opt.generate():
        metric = [function(p) for p in population]
        opt.update(metric)

    assert abs(y - function(opt.minimal)) < 1e-2
    # assert y == pytest.approx(function(opt.minimal), 0.01)


if __name__ == '__main__':
    pytest.main()
