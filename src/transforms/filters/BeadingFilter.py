from typing import List

import numpy as np

from transforms.filters.Filter import Filter


class BeadingFilter(Filter):
    def __init__(self, frequencies: List[int], **kwargs):
        Filter.__init__(self)
        self.frequencies = frequencies
        self.noise_floor = 0.1

    def apply(self, fs, buffer):
        n = len(buffer)
        ratio = float(n) / fs
        bases = np.where(np.abs(buffer) > self.noise_floor)[0]

        zero_index = int(float(n) / 2)

        bases_pos = bases[np.where(bases > zero_index)]
        bases_neg = bases[np.where(bases < zero_index)]

        buf = buffer

        for freq in self.frequencies:
            diff = int(freq * ratio)
            component = np.zeros(n, dtype='complex128')
            component[bases_pos+diff] = buffer[bases_pos]
            component[bases_neg-diff] = buffer[bases_neg]
            buf = buf + component
        return buf
