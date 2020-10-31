import numpy as np

from parameters.Parameter import Parameter


class SlidingParameter(Parameter):
    def __init__(self, start, end, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.start = start
        self.end = end

    def sample(self, fs, start, end):
        return np.sin(np.linspace(0, 110*np.pi, end-start))