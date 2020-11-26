import numpy as np

from custom_types import Frames
from sources.Source import Source


class SawSource(Source):
    def __init__(self, freq, seconds, **kwargs):
        Source.__init__(self)
        self.freq = freq
        self.per = 1.0 / float(self.freq)
        self.seconds = seconds

    def get_buffer(self, fs: Frames, start: Frames, end: Frames):
        t = np.linspace(start, end, end-start)
        note = np.divide(np.mod(t, int(self.per*fs)), self.per*fs) * 2 - 1
        return note

    def get_duration(self, fs):
        return int(self.seconds * fs)

    def get_period(self, fs: Frames) -> Frames:
        return int(self.per * fs)
