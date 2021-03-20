from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, FrameRange, Hz
from mixins.domains import TemporalDomainHelper


class DilatedSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.child = context.resolved_refs['child']
        self.factor = float(context.data['factor'])

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        return self.child.get_temporal(fs * self.factor, start, end)

    def get_range(self, fs: Hz) -> FrameRange:
        return self.child.get_range(fs * self.factor)


register(
    name="dilated",
    ctor=DilatedSignal,
)
