from .transformer import Transformer
from enum import IntEnum
from functools import partial


class SsmDeformator(Transformer):
    class DeterminationUsage(IntEnum):
        """ Specify a rule to decide the explanatory which to use variables of
            statistical model to the extent.
        """
        ExplanatoryByTripleSigma = -2
        ExplanatoryByDoubleSigma = -1
        All = 0
        Number = 1

    def __init__(
        self,
        extent_rule=SsmDeformator.DeterminationUsage.ExplanatoryByDoubleSigma
    ):
        self.extent_rule = int(extent_rule)
        self.extent_method = self.get_extent_method(self.extent_rule)

    def transform(self, model, x):
        ndim = self.extent_method(model)
        deformed = model['mean'] + \
            model['score'][..., :ndim] * x[:ndim]
        return deformed

    def get_extent_method(self, rule):
        usage_method = SsmDeformator.DeterminationUsage
        if rule == usage_method.ExplanatoryByDoubleSigma:
            return partial(self.make_explanatory_by_explanatory, threshold=95)
        elif rule == usage_method.ExplanatoryByTripleSigma:
            return partial(self.make_explanatory_by_explanatory, threshold=99)
        elif rule == usage_method.All:
            return lambda x: None
        elif rule > 0:
            return partial(self.make_explanatory_by_number, number=int(rule))
        else:
            raise ValueError('Unknown rule: {}'.format(rule))

    def make_explanatory_by_explanatory(self, model, threshold):
        total = 0.0
        for i, e in enumerate(model['explained']):
            total += e
            if total >= threshold:
                return i
        return len(model['explained'])

    def make_explanatory_by_number(self, model, number):
        return number
