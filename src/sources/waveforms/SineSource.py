import numpy as np

from sources.Source import Source


class SineSource(Source):
    def __init__(self, freq, seconds):
        Source.__init__(self)
        self.freq = freq
        self.seconds = seconds

    def get_buffer(self, fs, start, end):
        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        t = np.linspace(0, self.seconds, int(self.seconds * fs), False)
        note = np.sin(self.freq * t * 2 * np.pi)
        return note[start:end]

    def get_duration(self, fs):
        return int(self.seconds * fs)
