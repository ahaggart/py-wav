import numpy as np

from SignalData import SignalData
from custom_types import Frames
from mixins.domains import TemporalDomainHelper
from signals.DerivedSignal import DerivedSignal


class ScaledSignal(TemporalDomainHelper, DerivedSignal):
    def __init__(self, data: SignalData):
        TemporalDomainHelper.__init__(self)
        DerivedSignal.__init__(self, data, 'child')
        self.factor = self.data.resolved_refs['factor']

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        return np.multiply(
            self.child.get_temporal(fs, start, end),
            self.factor.get_temporal(fs, start, end),
        )
