import numpy as np
from sources.Source import Source


class SawSource(Source):
    def __init__(self, freq, seconds, **kwargs):
        Source.__init__(self)
        self.create_mapping(type_name='s_saw')
        self.freq = freq
        self.per = 1.0 / float(self.freq)
        self.seconds = seconds

    def get_buffer(self, fs, start, end):
        t = np.linspace(0, end-start, end-start) + start
        note = np.divide(np.mod(t, int(self.per*fs)), self.per*fs) * 2 - 1
        return note

    def get_duration(self, fs):
        return int(self.seconds * fs)