import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Hz, Partial, FrameRange, Frames
from mixins.buffers import TilingMixin, TruncatingMixin
from mixins.domains import TemporalDomainHelper


class ConstantSignal(TruncatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.value = float(self.data.data['value'])
        self.dur = float(self.data.data['dur'])

    def get_temporal_checked(self, fs: Hz, start: Frames, end: Frames):
        return np.full(end-start, self.value)

    def get_range(self, fs: Hz) -> FrameRange:
        return 0, self.dur * fs


register(
    name="constant",
    ctor=ConstantSignal,
)
