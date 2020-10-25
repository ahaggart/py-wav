import numpy as np
import math


class Note:
    def __init__(self, wav):
        self.wav = wav
        self.fs = fs

    def sample(self, t):
        return self.wav[t%len(wav)]


class PureNote:
    def __init__(self, freq, fs):
        self.freq = freq
        self.fs = fs
        self.step = freq * 2 * np.pi / fs

    def sample(self, t):
        return math.sin(t * self.step)

    def record(self, ns):
        return [self.sample(t) for t in range(0, ns * self.fs)]
            
