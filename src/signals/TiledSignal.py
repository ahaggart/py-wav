from Signal import Signal
from SignalData import SignalData
from custom_types import FrameRange, Frames
from mixins.buffers import TilingMixin
from mixins.domains import TemporalDomainHelper


class TiledSignal(TilingMixin, TemporalDomainHelper, Signal):
    def __init__(self, data: SignalData):
        Signal.__init__(self, data)
        TemporalDomainHelper.__init__(self)
        TilingMixin.__init__(self)
        self.child = self.data.resolved_refs['child']
        self.direction = self.data.data['direction']

        if self.direction not in ['forward', 'backward', 'both']:
            raise ValueError( f"Given direction {self.direction} is not valid")

    def get_range(self, fs: Frames) -> FrameRange:
        lower, upper = self.child.get_range(fs)
        if self.direction == 'forward':
            return lower, None
        elif self.direction == 'backward':
            return None, upper
        else:
            return None, None

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs)

    def get_buffer(self, fs: Frames):
        lower, upper = self.child.get_range(fs)
        period = self.child.get_period(fs)
        if lower is not None:
            return self.child.get_temporal(fs, lower, lower+period)
        elif upper is not None:
            return self.child.get_temporal(fs, upper-period, upper)
        else:
            return self.child.get_temporal(fs, 0, period)
