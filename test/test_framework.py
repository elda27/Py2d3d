import pytest
from contextlib import ExitStack

from framework.framework import Framework


class TrialFramework(Framework):
    def __init__(self, pre_value, post_value):
        self.pre_value = pre_value
        self.post_value = post_value

    def generate_pre(self, value):
        assert self.pre_value == value
        return value + 1

    def generate_post(self, value):
        assert self.post_value == value
        return value + 2


@pytest.mark.parametrize('start, pre, post, last', [
    (10, 11, 14, 16)
])
def test_framework(start, pre, post, last):
    framework = TrialFramework(start, post)
    generator = framework.generate(start)

    try:
        value = next(generator)
        assert value == pre
        value = generator.send(value + 3)
        assert value == last
    except StopIteration:
        pass


if __name__ == '__main__':
    pytest.main()
