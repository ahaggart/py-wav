from typing import List

import numpy as np

from transforms.filters.Filter import Filter


class BeadingFilter(Filter):
    def __init__(self, degrees: List[int], **kwargs):
        Filter.__init__(self)
        self.create_params()

        self.degrees = degrees
        self.noise_floor = 0.1

    def apply(self, fs, buffer):
        n = len(buffer)
        ratio = float(n) / fs
        bases = np.where(np.abs(buffer) > self.noise_floor)[0]

        buf = buffer

        for degree in self.degrees:
            diff = int(degree * ratio)
            component = np.zeros(n, dtype='complex128')
            component[bases+diff] = buffer[bases]
            component[bases-diff] = buffer[bases]
            buf = buf + component
        return buf
