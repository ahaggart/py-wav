import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Hz, FrameRange, Frames, Seconds
from mixins.buffers import TruncatingMixin
from mixins.domains import TemporalDomainHelper


class ConstantSignal(TruncatingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.value = float(self.data.data['value'])
        self.dur = Seconds(self.data.data['dur'])
        self.fs = int(self.data.data['fs'])

    def get_temporal_checked(self, start: Frames, end: Frames):
        return np.full(end-start, self.value)

    def get_range(self) -> FrameRange:
        return 0, self.dur * self.fs

    def get_fs(self) -> Frames:
        return self.fs


register(
    name="constant",
    ctor=ConstantSignal,
)
