import numpy as np

from sources.Source import Source


class SineSource(Source):
    def __init__(self, freq, seconds, **kwargs):
        Source.__init__(self)
        self.freq = freq
        self.seconds = seconds

    def get_buffer(self, fs, start, end):
        # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
        dur = float(end-start) / fs
        t = np.linspace(0, 2*np.pi*self.freq*dur, end-start)
        return np.sin(t+float(start)/fs)

    def get_duration(self, fs):
        return int(self.seconds * fs)
