import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, Hz, FrameRange, Seconds
from mixins.buffers import TruncatingMixin
from mixins.domains import TemporalDomainHelper


class SineSignal(TruncatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.freq = Hz(self.data.data['freq'])
        self.dur = Seconds(self.data.data['dur'])
        self.fs = int(self.data.data['fs'])

    def get_temporal_checked(self, start: Frames, end: Frames):
        return np.sin(np.arange(start, end) * 2 * self.freq * np.pi / self.fs)

    def get_range(self) -> FrameRange:
        return 0, self.dur * self.get_fs()

    def get_fs(self) -> Frames:
        return self.fs


register(
    name="sine",
    ctor=SineSignal,
)
