import wave

import numpy as np

from custom_types import Frames
from sources.Source import Source


class WavSource(Source):
    def __init__(self, file, **kwargs):
        Source.__init__(self)
        self.file = file
        self.buffer = None
        self.source_fs = None

    def load_source(self):
        with wave.open(self.file, 'rb') as w:
            n_frames = w.getnframes()
            self.source_fs = w.getframerate()
            self.buffer = np.frombuffer(w.readframes(n_frames), dtype=np.int32)
            self.buffer = self.buffer * 1.0 / np.max(np.abs(self.buffer))

    def get_buffer(self, fs: int, start: int, end: int):
        if self.buffer is None:
            self.load_source()
        return self.buffer[start:end]

    def get_duration(self, fs) -> int:
        if self.buffer is None:
            self.load_source()
        return len(self.buffer)

    def get_period(self, fs: Frames) -> Frames:
        return self.get_duration(fs)
