import Domains
from Signal import Signal
from SignalContext import SignalContext
from SignalData import SignalData
from custom_types import Frames, FrameRange, Seconds
from mixins.DomainMixins import TemporalDomainHelper


class OffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext, data: SignalData):
        Signal.__init__(self, context, data)
        TemporalDomainHelper.__init__(self)

        self.child = self.context.manager.get_signal(
            uuid=self.data.data['child'],
            caller_uuid=self.data.uuid,
            primary_domain=Domains.TIME,
        )

        self.offset: Seconds = float(self.data.data['offset'])

    def get_offset_frames(self, fs: Frames) -> Frames:
        return int(fs * self.offset)

    def get_range(self, fs: Frames) -> FrameRange:
        child_lower, child_upper = self.child.get_range(fs)
        offset_frames = self.get_offset_frames(fs)

        if offset_frames > 0:
            lower = 0 if child_lower is not None else None
            upper = child_upper + offset_frames if child_upper is not None else None
        else:
            lower = child_lower + offset_frames if child_lower is not None else None
            upper = max(child_upper + offset_frames, 0) if child_upper is not None else None

        return lower, upper

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
