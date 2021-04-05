from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, FrameRange, Seconds, Hz, Partial
from mixins.domains import TemporalDomainHelper
from util.frames import to_frames


class OffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)

        self.child = self.data.resolved_refs['child']
        self.offset: Seconds = Seconds(self.data.data['offset'])

    def get_offset_frames(self, fs: Hz) -> Partial:
        return fs * self.offset

    def get_range(self, fs: Hz) -> FrameRange:
        child_lower, child_upper = self.child.get_range(fs)
        offset_frames = self.get_offset_frames(fs)

        return child_lower+offset_frames, child_upper+offset_frames

    def get_temporal(self, fs: Hz, size: Frames, end: Frames):
        offset_frames = to_frames(self.get_offset_frames(fs))
        sample_end = to_frames(end - self.get_offset_frames(fs))
        return self.child.get_temporal(fs, size, sample_end)


register(
    name="offset",
    ctor=OffsetSignal,
)
