import pytest
import numpy as np
import sys
from io import StringIO

from objective_function import monophasic
import optimizer
import framework


@pytest.mark.parametrize('function, x, y', [
    (monophasic, [0.0, 0.0, 0.0, 0.0], 0.0,)
])
def test_cma_es(function, x, y):
    x = np.asarray(x)

    opt = optimizer.CmaEsOptimizer()
    opt.add_framework(framework.TqdmReport())

    x0 = np.random.random(x.shape)
    opt.set_initial_guess(x0)
    opt.set_hyper_parameters(sigma=1.0)
    with opt.setup():
        for population in opt.generate():
            metric = [function(p) for p in population]
            opt.update(metric)

    assert abs(y - function(opt.minimal)) < 1e-2


if __name__ == '__main__':
    pytest.main()
