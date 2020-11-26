from typing import List, Tuple

import numpy as np

from SourceState import SourceState
from custom_types import Frames
from samplers.OffsetSampler import OffsetSampler
from samplers.Sampler import Sampler
from sources.Source import Source


class AdditiveSource(Source):
    def __init__(self, children: List[Tuple[float, Source]] = None, **kwargs):
        Source.__init__(self)
        self.create_mapping(type_name='additive')
        self.children = children if children is not None else []

    def with_source(self, offset: float, source: Source):
        self.children.append((offset, source))
        return self

    def get_buffer(self, fs, start, end):
        buffer = np.zeros(end-start)
        for offset, child in self.children:
            # offset_frames = int(offset*fs)
            # child_start = max(start - offset_frames, 0)
            # child_end = min(end + offset_frames, end)
            # buffer[child_start:child_end] += child.get_buffer(fs, child_start, child_end)
            buffer += child.sample(fs, self.state.offset, start, end)
        return buffer

    def get_duration(self, fs) -> int:
        # return max([child.get_duration(fs) + int(offset * fs) for offset, child in self.children])
        raise DeprecationWarning

    def set_sampler(self, sampler: Sampler):
        super().set_sampler(sampler)
        for offset, child in self.children:
            child.set_sampler(OffsetSampler(offset, sampler))

    def set_state(self, state: SourceState):
        super().set_state(state)
        for offset, child in self.children:
            child.set_state(self.state.with_offset(offset))

    def get_period(self, fs: Frames) -> Frames:
        return max((offset*fs + child.get_period(fs) for offset, child in self.children))
