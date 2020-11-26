from typing import List

import numpy as np
from bezier import Curve

from sources.Source import Source


class BezierSource(Source):
    def __init__(self, seconds: float, freq: float, points: List[List[float]], **kwargs):
        Source.__init__(self)
        self.seconds = seconds
        self.freq = float(freq)
        self.points = np.array(points)
        self.curve = Curve.from_nodes(points)

    def get_duration(self, fs) -> int:
        return int(self.seconds * fs)

    def get_buffer(self, fs: int, start: int, end: int):
        # steps = np.mod(np.linspace(0, 1, self.get_duration(fs)), 2) / 2
        dur = self.get_duration(fs)
        t = np.linspace(0, 1, dur)
        per = int(fs / self.freq)
        steps = np.linspace(np.min(self.points[0]), np.max(self.points[0]), per)
        x = self.curve.evaluate_multi(t)[0]
        y = self.curve.evaluate_multi(t)[1]
        wave = np.interp(steps, x, y)
        print(wave.shape)
        buffer = np.tile(wave, int(float(dur)/per + 1))
        return buffer[start:end]
