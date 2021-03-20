import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, FrameRange, Hz, Partial
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper
from util.buffer import get_centered_sample


class DilatedSignal(TilingMixin, TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)
        self.child = context.resolved_refs['child']
        self.factor = float(context.data['factor'])

    def get_buffer(self, fs: Hz):
        return get_centered_sample(self.child, fs * self.factor)

    def get_range(self, fs: Hz) -> FrameRange:
        return self.child.get_range(fs * self.factor)

    def get_period(self, fs: Hz) -> Partial:
        return self.child.get_period(fs * self.factor)


register(
    name="dilated",
    ctor=DilatedSignal,
)
