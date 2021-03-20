import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Hz, Partial, FrameRange, Frames
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper


class ConstantSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.value = float(self.data.data['value'])

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        return np.full(end-start, self.value)

    def get_period(self, fs: Hz) -> Partial:
        return 1

    def get_range(self, fs: Hz) -> FrameRange:
        return None, None


register(
    name="constant",
    ctor=ConstantSignal,
)
