import numpy as np

from custom_types import Hz
from parameters.Parameter import Parameter


class BandPassParameter(Parameter):
    def __init__(self, lower: Hz, upper: Hz, param: Parameter, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.lower = lower
        self.upper = upper
        self.param = param

    def sample(self, fs, start, end):
        base = self.param.sample(fs, start, end)
        step_hz = float(fs) / len(base)
        flt = np.zeros(len(base))
        center = int(len(base) / 2)

        step_lower = int(self.lower / step_hz)
        step_upper = int(self.upper / step_hz)

        flt[center+step_lower:center+step_upper] = 1
        flt[center-step_upper:center-step_lower] = 1

        return flt * base
