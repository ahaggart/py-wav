import numpy as np

from parameters.Parameter import Parameter


def split_dft(dft):
    n = len(dft)
    return np.concatenate([dft[int(n / 2):], dft[:int(n / 2)]])


class FourierInverseParameter(Parameter):
    def __init__(self, param: Parameter, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.param = param

    @staticmethod
    def get_inverse_dft(fs, buffer):
        return np.real(np.fft.ifft(split_dft(buffer)) * fs)

    def sample(self, fs, start, end):
        src = self.param.sample(fs, start, end)
        return FourierInverseParameter.get_inverse_dft(fs, src)


class FourierParameter(Parameter):
    def __init__(self, param: Parameter, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.param = param

    @staticmethod
    def get_dft(fs, buffer):
        return split_dft(np.fft.fft(buffer) / fs)

    def sample(self, fs, start, end):
        src = self.param.sample(fs, start, end)
        return FourierParameter.get_dft(fs, src)
