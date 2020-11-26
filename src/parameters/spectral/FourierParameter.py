import numpy as np

from SourceState import SourceState
from custom_types import Frames
from parameters.Parameter import Parameter
from parameters.spectral.SpectralDomainParameter import SpectralDomainParameter
from sources.Source import Source


def split_dft(dft):
    n = len(dft)
    return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])


class FourierInverseParameter(Parameter):
    def __init__(self, param: SpectralDomainParameter, **kwargs):
        Parameter.__init__(self)
        self.param = param

    @staticmethod
    def get_inverse_dft(fs, buffer):
        return np.real(np.fft.ifft(split_dft(buffer)) * fs)

    def get_buffer(self, fs, start, end):
        src = self.param.get_buffer(fs)
        time_domain = FourierInverseParameter.get_inverse_dft(fs, src)
        return time_domain[start:end]


class FourierParameter(SpectralDomainParameter):
    def __init__(self, source: Source, **kwargs):
        SpectralDomainParameter.__init__(self)
        self.source = source

    @staticmethod
    def get_dft(fs, buffer):
        return split_dft(np.fft.fft(buffer) / fs)

    def get_buffer(self, fs: Frames):
        src = self.source.get_buffer(fs, 0, self.source.get_period(fs))
        return FourierParameter.get_dft(fs, src)

    def get_period(self, fs: Frames) -> Frames:
        return self.source.get_period(fs)

    def get_state(self) -> SourceState:
        return self.source.state
