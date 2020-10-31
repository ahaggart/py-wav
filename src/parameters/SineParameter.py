import numpy as np

from parameters.Parameter import Parameter


class SineParameter(Parameter):
    def __init__(self, freq: float, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.freq = freq

    def sample(self, fs, start, end):
        t = np.linspace(0, 2*np.pi*self.freq, end-start)
        return np.sin(t+float(start)/fs)
