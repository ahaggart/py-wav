import numpy as np

from custom_types import Frames
from parameters.Parameter import Parameter
from sources.Source import Source


class SourceParameter(Parameter):
    def __init__(self, source: Source, **kwargs):
        Parameter.__init__(self)
        self.source = source

    def get_buffer(self, fs, start, end):
        signal = self.source.get_buffer(fs, start, end)
        normalized = (signal - np.min(signal)) / np.ptp(signal)
        return normalized

    def sample_out(self, fs, start, end):
        return self.get_buffer(fs, start, end)

    def get_period(self, fs: Frames) -> Frames:
        return self.source.get_period(fs)
