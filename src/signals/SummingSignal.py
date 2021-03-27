import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from custom_types import FrameRange, Hz, Frames
from mixins.domains import TemporalDomainHelper


class SummingSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.children = self.data.resolved_refs['children']

    def get_range(self, fs: Hz) -> FrameRange:
        ranges = [c.get_range(fs) for c in self.children]
        upper = max((upper for _, upper in ranges))
        lower = min((lower for _, lower in ranges))
        return lower, upper

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        buf = np.zeros(end-start)
        for child in self.children:
            buf += child.get_temporal(fs, start, end)
        return buf
