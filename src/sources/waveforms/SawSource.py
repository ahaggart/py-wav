import numpy as np
from sources.Source import Source


class SawSource(Source):
    def __init__(self, freq, seconds, **kwargs):
        Source.__init__(self)
        self.create_params()
        self.freq = freq
        self.per = 1.0 / float(self.freq)
        self.seconds = seconds

    def get_buffer(self, fs, start, end):
        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        t = np.linspace(0, self.seconds*fs, int(self.seconds * fs), False)
        note = np.divide(np.mod(t, int(self.per*fs)), self.per*fs)
        return note[start:end]

    def get_duration(self, fs):
        return int(self.seconds * fs)