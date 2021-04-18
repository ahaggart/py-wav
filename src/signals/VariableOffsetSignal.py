import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from custom_types import Frames, FrameRange
from mixins.domains import TemporalDomainHelper
from util.buffer import get_centered_sample
from util.frames import to_frames, np_to_frames
from util.graph import verify_fs


class VariableOffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.child = self.data.resolved_refs['child']
        self.offset = self.data.resolved_refs['offset']
        verify_fs(child=self.child, offset=self.offset)

    def get_fs(self):
        return self.child.get_fs()

    def get_temporal(self, start: Frames, end: Frames):
        fs = self.get_fs()
        offsets_seconds = self.offset.get_temporal(start, end)
        offsets_partials = offsets_seconds * fs
        offsets_absolute = np.arange(start, end) - offsets_partials
        offsets_frames = np_to_frames(offsets_absolute)

        sample_start = np.min(offsets_frames)
        sample_end = np.max(offsets_frames) + 1
        sample = self.child.get_temporal(sample_start, sample_end)

        return sample[offsets_frames - sample_start]

    def get_range(self) -> FrameRange:
        """
        For bounded child and bounded parameter, sample the parameter to
        compute the lower and upper extent.
        """
        child_lower, child_upper = self.child.get_range()

        return self.calculate_extent(
            to_frames(child_lower), to_frames(child_upper)
        )

    def calculate_extent(self,
                         child_lower: Frames,
                         child_upper: Frames):
        fs = self.get_fs()
        offset_sample = np_to_frames(get_centered_sample(self.offset))
        offset_max = np.max(offset_sample)
        offset_min = np.min(offset_sample)

        # arrangement:
        #  ... | offset_min | child range | offset_max | ...
        offset_seconds = self.offset.get_temporal(
            child_lower+offset_min,
            child_upper+offset_max,
        )

        offset_partials = offset_seconds * fs
        position_frames = np.arange(len(offset_partials))
        sample_frames = np_to_frames(position_frames-offset_partials)

        in_range = np.logical_and(
            sample_frames >= -offset_min,
            sample_frames < child_upper-offset_min,
        )

        lower_idx = np.argmax(in_range)
        upper_idx = len(in_range) - np.argmax(in_range[::-1]) - 1

        lower = min(child_lower + offset_min + lower_idx, child_lower)
        upper = max(child_lower + offset_min + upper_idx + 1, child_upper)

        return lower, upper


register(
    name="var_offset",
    ctor=VariableOffsetSignal,
)
