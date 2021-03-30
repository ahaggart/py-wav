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

    def get_temporal(self, fs: Hz, size: Frames, end: Frames):
        # print(f"sampling {size} frames up to {end} @ {fs}")
        return np.multiply(
            self.child.get_temporal(fs, size, end),
            self.factor.get_temporal(fs, size, end),
        )


register(
    name="scaled",
    ctor=ScaledSignal,
)
