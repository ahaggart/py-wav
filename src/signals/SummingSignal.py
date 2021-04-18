import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from custom_types import FrameRange, Hz, Frames
from mixins.domains import TemporalDomainHelper
from util.graph import verify_fs


class SummingSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        self.children = self.data.resolved_refs['children']
        verify_fs(*self.children)
        self.fs = self.children[0].get_fs()

    def get_fs(self):
        return self.fs

    def get_range(self) -> FrameRange:
        ranges = [c.get_range() for c in self.children]
        upper = max((upper for _, upper in ranges))
        lower = min((lower for _, lower in ranges))
        return lower, upper

    def get_temporal(self, start: Frames, end: Frames):
        buf = np.zeros(end-start)
        for child in self.children:
            buf += child.get_temporal(start, end)
        return buf
