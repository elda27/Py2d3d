import pytest
import optimizer
import numpy as np
from objective_function import rosenbrock_function


@pytest.mark.parametrize('function, x, y, options', [
    ()
])
def test_cma_es(function, x, y, options):
    x = np.asarray(x)

    opt = optimizer.CmaEsOptimizer()

    x0 = np.random.random(x.shape)
    opt.set_initial_guess(x0)
    opt.set_hyper_parameters(sigma=1.0)
    opt.setup()
    for population in opt.generate():
        metric = [function(p) for p in population]
        opt.update(metric)

    assert abs(y - function(opt.minimal)) < 1e-2


if __name__ == '__main__':
    pytest.main()
