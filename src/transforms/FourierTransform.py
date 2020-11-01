from typing import List

import numpy as np

from parameters.Parameter import parametrize
from transforms.Transform import Transform
from transforms.filters.Filter import Filter


class FourierTransform(Transform):
    def __init__(self, filters: List[Filter], intensity=1, **kwargs):
        Transform.__init__(self)
        self.create_mapping()
        self.filters = filters
        self.intensity = parametrize(intensity)

    def split_dft(self, dft):
        n = len(dft)
        return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])

    def get_dft(self, fs, buffer):
        return self.split_dft(np.fft.fft(buffer) / fs)

    def apply(self, fs, buffer):
        dft = self.get_dft(fs, buffer)

        for f in self.filters:
            dft = f.apply(fs, dft)

        result = np.real(np.fft.ifft(self.split_dft(dft))) * fs

        result /= np.max(np.abs(result))

        intensity = self.intensity.sample_out(fs, 0, len(buffer))

        return result * intensity + buffer * (1-intensity)
