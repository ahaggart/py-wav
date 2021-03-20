import numpy as np

from SignalContext import SignalContext
from SignalRegistry import register, RegistryEntry
from custom_types import Frames, Hz
from mixins.domains import TemporalDomainHelper
from signals.DerivedSignal import DerivedSignal


class ScaledSignal(TemporalDomainHelper, DerivedSignal):
    def __init__(self, context: SignalContext):
        TemporalDomainHelper.__init__(self)
        DerivedSignal.__init__(self, context, 'child')
        self.factor = self.data.resolved_refs['factor']

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        return np.multiply(
            self.child.get_temporal(fs, start, end),
            self.factor.get_temporal(fs, start, end),
        )


register(
    name="scaled",
    ctor=ScaledSignal,
)
