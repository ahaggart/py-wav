import numpy as np

from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, Hz, Partial, FrameRange
from mixins.domains import TemporalDomainHelper


class SineSignal(TemporalDomainHelper, Signal):
    def __init__(self, data: SignalData):
        Signal.__init__(self, data)
        TemporalDomainHelper.__init__(self)
        self.freq = Hz(self.data.data['freq'])

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        return np.sin(np.arange(start, end) * 2 * self.freq * np.pi / fs)

    def get_period(self, fs: Hz) -> Partial:
        return fs / self.freq

    def get_range(self, fs: Hz) -> FrameRange:
        return None, None
