from Signal import Signal
from SignalData import SignalData
from custom_types import Frames, FrameRange, Seconds
from mixins.domains import TemporalDomainHelper


class OffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, data: SignalData):
        Signal.__init__(self, data)
        TemporalDomainHelper.__init__(self)

        self.child = self.data.resolved_refs['child']
        self.offset: Seconds = Seconds(self.data.data['offset'])

    def get_offset_frames(self, fs: Frames) -> Frames:
        return int(fs * self.offset)

    def get_range(self, fs: Frames) -> FrameRange:
        child_lower, child_upper = self.child.get_range(fs)
        offset_frames = self.get_offset_frames(fs)

        if child_upper is None or child_lower is None:
            return child_lower, child_upper
        else:
            if offset_frames > 0:
                return child_lower, child_upper + offset_frames
            else:
                return child_lower + offset_frames, child_upper

    def get_period(self, fs: Frames) -> Frames:
        """Return the period of the offset signal.

        If the child signal is unbounded, return the child's period.
        If the child signal is bounded, return the range as period.
        """
        lower, upper = self.get_range(fs)
        if lower is None or upper is None:
            return self.child.get_period(fs)
        return upper - lower

    def get_temporal(self, fs: Frames, start: Frames, end: Frames):
        offset_frames = self.get_offset_frames(fs)
        return self.child.get_temporal(fs, start-offset_frames, end-offset_frames)
