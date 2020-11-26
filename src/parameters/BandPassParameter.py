import numpy as np

from custom_types import Hz, Frames
from parameters.Parameter import Parameter
from parameters.spectral.SpectralDomainParameter import SpectralDomainParameter


class BandPassParameter(SpectralDomainParameter):
    def __init__(self, lower: Hz, upper: Hz, param: SpectralDomainParameter, **kwargs):
        SpectralDomainParameter.__init__(self)
        self.create_mapping()
        self.lower = lower
        self.upper = upper
        self.param = param

    def get_buffer(self, fs):
        base = self.param.get_buffer(fs)
        step_hz = float(fs) / len(base)
        flt = np.zeros(len(base))
        center = int(len(base) / 2)

        step_lower = int(self.lower / step_hz)
        step_upper = int(self.upper / step_hz)

        flt[center+step_lower:center+step_upper] = 1
        flt[center-step_upper:center-step_lower] = 1

        return flt * base

    def get_period(self, fs: Frames) -> Frames:
        return self.param.get_period(fs)
