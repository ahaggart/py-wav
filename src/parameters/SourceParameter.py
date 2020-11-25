import numpy as np

from parameters.Parameter import Parameter
from sources.Source import Source


class SourceParameter(Parameter):
    def __init__(self, source: Source, **kwargs):
        Parameter.__init__(self)
        self.create_mapping()
        self.source = source

    def sample(self, fs, start, end):
        signal = self.source.get_buffer(fs, start, end)
        normalized = (signal - np.min(signal)) / np.ptp(signal)
        return normalized

    def sample_out(self, fs, start, end):
        return self.sample(fs, start, end)
