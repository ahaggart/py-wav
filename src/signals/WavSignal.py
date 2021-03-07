import wave

import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalData import SignalData
from custom_types import Frames, FrameRange
from mixins.BufferMixins import TilingMixin
from mixins.DomainMixins import TemporalDomainHelper


class WavSignal(TemporalDomainHelper, TilingMixin, Signal):
    def __init__(self, context: SignalContext, data: SignalData):
        Signal.__init__(self, context, data)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)
        self.file = data.data['file']
        self.buffer = None
        self.source_fs = None

    def load_source(self):
        with wave.open(self.file, 'rb') as w:
            n_frames = w.getnframes()
            self.source_fs = w.getframerate()
            self.buffer = np.frombuffer(w.readframes(n_frames), dtype=np.int32)
            self.buffer = self.buffer * 1.0 / np.max(np.abs(self.buffer))

    def scale_source(self, fs: Frames):
        x = np.linspace(0, 1, self.get_duration(fs))
        xp = np.linspace(0, 1, len(self.buffer))
        return np.interp(x, xp, self.buffer)

    def get_buffer(self, fs: Frames):
        if self.buffer is None:
            self.load_source()
        return self.scale_source(fs)

    def get_duration(self, fs: Frames) -> Frames:
        if self.buffer is None:
            self.load_source()
        return int((len(self.buffer) * fs) / self.source_fs)

    def get_period(self, fs: Frames) -> Frames:
        return self.get_duration(fs)

    def get_range(self, fs: Frames) -> FrameRange:
        return 0, self.get_duration(fs)
