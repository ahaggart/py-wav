import numpy as np

from custom_types import Frames
from mixins.BufferMixins import TilingMixin


def split_dft(dft):
    n = len(dft)
    return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])


def to_spectral(fs: Frames, buffer):
    return split_dft(np.fft.fft(buffer) / fs)


def to_temporal(fs: Frames, buffer):
    return np.real(np.fft.ifft(split_dft(buffer))) * fs


class TemporalDomainHelper:
    """Utility mixin for signals defined in primarily in the temporal domain.
    @DynamicAttrs
    """
    def get_spectral(self, fs: Frames):
        lower, upper = self.get_range(fs)
        period = self.get_period(fs)
        if lower is not None:
            buffer = self.get_temporal(fs, lower, lower+period)
        elif upper is not None:
            buffer = self.get_temporal(fs, upper-period, upper)
        else:
            buffer = self.get_temporal(fs, 0, period)
        return to_spectral(fs, buffer)


class SpectralDomainHelper(TilingMixin):
    """Utility mixin for signals defined primarily in the spectral domain.
    @DynamicAttrs
    """
    def get_buffer(self, fs: Frames):
        return to_temporal(fs, self.get_spectral(fs))
