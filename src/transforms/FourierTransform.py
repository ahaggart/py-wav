from typing import List

import numpy as np

from transforms.Transform import Transform
from transforms.filters.Filter import Filter


def apply_filter(dft, filter):
    n = len(dft)
    filter_split = np.concatenate([filter[int(n / 2):], filter[:int(n / 2)]])
    return dft * filter_split


class FourierTransform(Transform):
    def __init__(self, filters: List[Filter], **kwargs):
        Transform.__init__(self)
        self.create_params()
        self.filters = filters

    def split_dft(self, dft):
        n = len(dft)
        return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])

    def get_dft(self, fs, buffer):
        return self.split_dft(np.fft.fft(buffer) / fs)

    def apply(self, fs, buffer):
        dft = self.get_dft(fs, buffer)

        for f in self.filters:
            dft = f.apply(fs, dft)

        return np.real(np.fft.ifft(self.split_dft(dft)))
