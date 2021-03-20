from typing import Optional

import numpy as np

from Signal import Signal
from SignalContext import SignalContext
from SignalRegistry import register
from core.throwables import AperiodicResultException
from custom_types import Hz, Frames, FrameRange, Partial
from mixins.domains import TemporalDomainHelper
from util.buffer import get_valid_range, get_centered_sample
from util.frames import to_frames, np_to_frames


class VariableOffsetSignal(TemporalDomainHelper, Signal):
    def __init__(self, context: SignalContext):
        Signal.__init__(self, context)
        TemporalDomainHelper.__init__(self)
        self.child = self.data.resolved_refs['child']
        self.offset = self.data.resolved_refs['offset']

    def get_temporal(self, fs: Hz, start: Frames, end: Frames):
        offsets_seconds = self.offset.get_temporal(fs, start, end)
        offsets_partials = offsets_seconds * fs
        offsets_absolute = np.arange(start, end) - offsets_partials
        offsets_frames = np_to_frames(offsets_absolute)

        sample_start = np.min(offsets_frames)
        sample_end = np.max(offsets_frames) + 1
        sample = self.child.get_temporal(fs, sample_start, sample_end)

        return sample[offsets_frames - sample_start]

    def get_range(self, fs: Hz) -> FrameRange:
        """
        For bounded child and bounded parameter, sample the parameter to
        compute the lower and upper extent.
        """
        child_lower, child_upper = self.child.get_range(fs)

        return self.calculate_extent(
            fs, to_frames(child_lower), to_frames(child_upper)
        )

    def calculate_extent(self,
                         fs: Hz,
                         child_lower: Frames,
                         child_upper: Frames):
        offset_sample = np_to_frames(get_centered_sample(self.offset, fs))
        offset_max = np.max(offset_sample)
        offset_min = np.min(offset_sample)

        # arrangement:
        #  ... | offset_min | child range | offset_max | ...
        offset_seconds = self.offset.get_temporal(
            fs,
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

    def get_max_offset(self, fs: Hz, start: Frames, end: Frames):
        offsets = get_centered_sample(self.offset, fs) * fs
        positions = np.arange(len(offsets)) * fs
        return np.max(offsets+positions)


register(
    name="var_offset",
    ctor=VariableOffsetSignal,
)
