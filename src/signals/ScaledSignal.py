import numpy as np

from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, Hz
from mixins.domains import TemporalDomainHelper
from signals.DerivedSignal import DerivedSignal


class ScaledSignal(TemporalDomainHelper, DerivedSignal):
    def __init__(self, context: SignalContext):
        TemporalDomainHelper.__init__(self)
        DerivedSignal.__init__(self, context, 'child')
        self.factor = self.data.resolved_refs['factor']

        if self.factor.get_fs() != self.child.get_fs():
            raise ValueError(f"factor fs={self.factor.get_fs()} "
                             f"does not match child fs={self.child.get_fs()}")

    def get_temporal(self, start: Frames, end: Frames):
        return np.multiply(
            self.child.get_temporal(start, end),
            self.factor.get_temporal(start, end),
        )


register(
    name="scaled",
    ctor=ScaledSignal,
)
