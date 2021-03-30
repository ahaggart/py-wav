import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, Hz, Partial, FrameRange, Seconds
from mixins.buffers import TruncatingMixin
from mixins.domains import TemporalDomainHelper
from util.frames import to_frames


class SineSignal(TruncatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.freq = Hz(self.data.data['freq'])
        self.dur = Seconds(self.data.data['dur'])

    def get_temporal_checked(self, fs: Hz, size: Frames, end: Frames):
        return np.sin(np.arange(to_frames(end)-size, to_frames(end)) * 2 * self.freq * np.pi / fs)

    def get_range(self, fs: Hz) -> FrameRange:
        return 0, self.dur * fs


register(
    name="sine",
    ctor=SineSignal,
)
