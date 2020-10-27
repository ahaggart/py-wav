import numpy as np

from transforms.Transform import Transform


def apply_filter(dft, filter):
    n = len(dft)
    filter_split = np.concatenate([filter[int(n / 2):], filter[:int(n / 2)]])
    return dft * filter_split


class FourierTransform(Transform):
    def __init__(self, **kwargs):
        Transform.__init__(self)
        self.create_params()

    def apply(self, fs, buffer):
        n = len(buffer)
        dft = np.fft.fft(buffer)

        filter = np.zeros(n)
        filter.fill(0.2)
        modifier = 16
        half_modifier = int(modifier / 2)
        filter[(half_modifier-1)*int(n/modifier):(half_modifier+1)*int(n/modifier)] = 1
        dft_filtered = apply_filter(dft, filter)

        return np.abs(np.fft.ifft(dft_filtered))
