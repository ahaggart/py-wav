from typing import Any, NewType, Union

import numpy as np

from core.Stateful import Stateful
from custom_types import Frames, Seconds
from mapper.Mappable import Mappable
from sources.Source import Source


class Parameter(Source):
    def __init__(self):
        Stateful.__init__(self)

    def get_buffer(self, fs, start, end):
        raise NotImplementedError

    def get_period(self, fs: Frames) -> Frames:
        raise NotImplementedError


class ConstantParameter(Parameter):
    def __init__(self, value: int, **kwargs):
        Parameter.__init__(self)
        self.value = value

    def get_buffer(self, fs, start, end):
        return np.ones(end-start) * self.value

    def get_period(self, fs: Frames) -> Frames:
        return -1  # constant parameters do not have a period


Parametrizable = NewType("parametrizable", Union[int, float, Parameter])


def parametrize(p: Parametrizable) -> Parameter:
    if isinstance(p, Parameter):
        return p
    elif isinstance(p, (int, float)):
        return ConstantParameter(p)

    raise TypeError

