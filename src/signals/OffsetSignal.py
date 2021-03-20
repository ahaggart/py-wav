from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, FrameRange, Seconds, Hz, Partial
from mixins.domains import TemporalDomainHelper
from util.frames import to_frames


class OffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)

        self.child = self.data.resolved_refs['child']
        self.offset: Seconds = Seconds(self.data.data['offset'])

    def get_offset_frames(self, fs: Hz) -> Partial:
        return fs * self.offset

    def get_range(self, fs: Hz) -> FrameRange:
        child_lower, child_upper = self.child.get_range(fs)
        offset_frames = self.get_offset_frames(fs)

        if offset_frames > 0:
            return (
                child_lower,
                child_upper + offset_frames if child_upper is not None else None,
            )
        else:
            return (
                child_lower + offset_frames if child_lower is not None else None,
                child_upper,
            )

    def get_period(self, fs: Hz) -> Partial:
        """Return the period of the offset signal.

        If the child signal is unbounded, return the child's period.
        If the child signal is bounded, return the range as period.
        """
        lower, upper = self.get_range(fs)
        if lower is None or upper is None:
            return self.child.get_period(fs)
        return upper - lower

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        offset_frames = to_frames(self.get_offset_frames(fs))
        return self.child.get_temporal(fs, start-offset_frames, end-offset_frames)


register(
    name="offset",
    ctor=OffsetSignal,
)
