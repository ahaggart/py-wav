import numpy as np

from custom_types import Frames


def split_dft(dft):
    n = len(dft)
    return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])


def get_spectral(fs: Frames, buffer):
    return split_dft(np.fft.fft(buffer) / fs)


def get_temporal(fs: Frames, buffer):
    return np.real(np.fft.ifft(split_dft(buffer))) * fs


class SpectralMixin:
    """Utility mixin for signals defined in primarily in the temporal domain.
    @DynamicAttrs
    """
    def get_spectral(self, fs: Frames):
        buffer = self.get_temporal(fs, 0, self.get_period(fs))
        return get_spectral(fs, buffer)


class TemporalMixin:
    """Utility mixin for signals defined primarily in the spectral domain.
    @DynamicAttrs
    """
    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        buffer = get_temporal(fs, self.get_spectral(fs))
        tiled_buffer = np.tile(buffer, int((end-start)/len(buffer))+1)
        return tiled_buffer[start:end]
