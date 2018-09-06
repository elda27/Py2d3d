from .cma_es_optimizer import CmaEsOptimizer

_Optimizers = {
    'cma-es': CmaEsOptimizer
}


def make_optimizer(name):
    return _Optimizers[name]()
