import numpy as np

from custom_types import Frames, Hz
from mixins.buffers import TilingMixin
from util.buffer import get_centered_sample


def split_dft(dft):
    n = len(dft)
    return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])


def to_spectral(fs: Hz, buffer):
    return split_dft(np.fft.fft(buffer) / fs)


def to_temporal(fs: Hz, buffer):
    return np.real(np.fft.ifft(split_dft(buffer))) * fs


class TemporalDomainHelper:
    """Utility mixin for signals defined in primarily in the temporal domain.
    @DynamicAttrs
    """
    def get_spectral(self, fs: Hz):
        buffer = get_centered_sample(self, fs)
        return to_spectral(fs, buffer)


class SpectralDomainHelper(TilingMixin):
    """Utility mixin for signals defined primarily in the spectral domain.
    @DynamicAttrs
    """
    def get_buffer(self, fs: Hz):
        return to_temporal(fs, self.get_spectral(fs))
