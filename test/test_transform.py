import pytest
import transform

Usage = transform.SsmDeformator.DeterminationUsage


@pytest.mark.parametrize('explain, ans', [
    ([99.5, 0.4, 0.01, 0.002, 0.001, 0.001, 1e-4], 3)
])
def test_extent_rule_triple_sigma(explain, ans):
    assert sum(explain) < 100
    deformator = transform.SsmDeformator(Usage.ExplanatoryByTripleSigma)
    dim = deformator.get_using_dimension({'explained': explain})
    assert dim == ans


@pytest.mark.parametrize('explain, ans', [
    ([70.5, 20.4, 7.2, 1.1, 0.001, 0.001, 1e-4], 3)
])
def test_extent_rule_triple_sigma(explain, ans):
    assert sum(explain) < 100
    deformator = transform.SsmDeformator(Usage.ExplanatoryByDoubleSigma)
    dim = deformator.get_using_dimension({'explained': explain})
    assert dim == ans
