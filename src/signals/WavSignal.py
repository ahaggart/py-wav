import wave

import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Hz, Frames, FrameRange
from mixins.buffers import TruncatingMixin
from mixins.domains import TemporalDomainHelper


class WavSignal(TemporalDomainHelper, TruncatingMixin, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.file = context.data['file']
        self.buffer = None
        self.fs: Hz = None

    def load_source(self):
        with wave.open(self.file, 'rb') as w:
            n_frames = w.getnframes()
            self.fs = w.getframerate()
            self.buffer = np.frombuffer(w.readframes(n_frames), dtype=np.int32)
            self.buffer = self.buffer * 1.0 / np.max(np.abs(self.buffer))

    def get_source_buffer(self):
        if self.buffer is None:
            self.load_source()
        return self.buffer

    def get_temporal_checked(self, start: Frames, end: Frames):
        if self.buffer is None:
            self.load_source()
        return self.buffer[start:end]

    def get_fs(self):
        if self.buffer is None:
            self.load_source()
        return self.fs

    def get_range(self) -> FrameRange:
        if self.buffer is None:
            self.load_source()
        return 0, len(self.buffer)


register(
    name="wav",
    ctor=WavSignal,
)
