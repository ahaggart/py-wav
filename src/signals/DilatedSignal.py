from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, FrameRange
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper


class DilatedSignal(TilingMixin, TemporalDomainHelper, Signal):
    def __init__(self, data: SignalData):
        Signal.__init__(self, data)
        TemporalDomainHelper.__init__(self)
        self.child = data.resolved_refs['child']
        self.factor = float(data.data['factor'])

    def get_buffer(self, fs: Frames):
        lower, upper = self.get_range(fs)
        return self.child.get_temporal(fs * self.factor, lower, upper)

    def get_range(self, fs: Frames) -> FrameRange:
        return self.child.get_range(fs * self.factor)

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs * self.factor)
