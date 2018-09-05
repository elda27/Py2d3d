import cma
from .optimizer import Optimizer


class CmaEsOptimizer(Optimizer):
    """Covariance Matrix Adaption-Evolution Strategy optimizer.

    Mainly hyper parameters are following:
        - sigma: A initial variance in order to generate population.
            This parameter likes the search range.
        - fixed_variables: dictionary with index-value pairs like 
            {0:1.1, 2:0.1} that are not optimized.
        - popsize: population size, AKA lambda, 
            number of new solution per iteration
        - CMA_stds: multipliers for sigma0 in each coordinate, 
            not represented in C, makes scaling_of_variables obsolete
        - randn: randn(lam, N) must return an np.array of shape (lam, N), 
            see also cma.utilities.math.randhss
    Other parmaeters indicated at line 407-480 
    in cma.evolution_strategy.py

    Please see the following for algorithm details.
    https://en.wikipedia.org/wiki/CMA-ES
    """

    def __init__(self):
        self.optimizer = None
        self.sigma = None
        self.options = cma.CMAOptions.defaults()

    def set_hyper_parameters(self, **params):
        self.sigma = params.pop('sigma')
        self.options.update(params)

    def setup(self):
        self.optimizer = cma.CMAEvolutionStrategy(
            self.initial_guess, self.sigma, self.options
        )

    def generate_core(self):
        self.population = self.optimizer.ask()
        return self.population

    def update_core(self, metric):
        self.optimizer.tell(self.population, metric)
        self.optimizing = self.optimizer.stop()
