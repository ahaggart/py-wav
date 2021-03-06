import numpy as np

from transforms.filters.Filter import Filter


class HarmonicFilter(Filter):
    def __init__(self, harmonics, noise_floor=0.1, **kwargs):
        Filter.__init__(self)
        self.harmonics = harmonics
        self.noise_floor = noise_floor

    def apply(self, fs, buffer):
        n = len(buffer)
        half_n = int(n/2)
        bases = np.where(np.abs(buffer) > self.noise_floor)

        buf = buffer

        for harmonic in self.harmonics:
            indices = (bases[0] - half_n) * harmonic + half_n
            # indices = np.concatenate([bases[0], bases[0] + 1, bases[0] - 1])
            component = np.zeros(n, dtype='complex128')
            component[indices] = buffer[bases]
            buf = buf + component / harmonic
        return buf

