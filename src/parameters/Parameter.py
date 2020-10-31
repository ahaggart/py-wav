from typing import Any

import numpy as np

from mapper.Mappable import Mappable


def parametrize(p: Any):
    if isinstance(p, Parameter):
        return p
    elif isinstance(p, int):
        return ConstantParameter(p)

    raise TypeError


class Parameter(Mappable):
    def __init__(self):
        Mappable.__init__(self)
        self.create_mapping()

    def sample(self, fs, start, end):
        raise NotImplementedError


class ConstantParameter(Parameter):
    def __init__(self, value: int, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()

        self.value = value

    def sample(self, fs, start, end):
        return np.ones(end-start) * self.value
