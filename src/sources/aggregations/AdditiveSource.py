from typing import List, Tuple

import numpy as np

from samplers.OffsetSampler import OffsetSampler
from samplers.Sampler import Sampler
from sources.Source import Source


class AdditiveSource(Source):
    def __init__(self, children: List[Tuple[float, Source]] = None):
        Source.__init__(self)
        self.children = children if children is not None else []

    def with_source(self, offset: float, source: Source):
        self.children.append((offset, source))
        return self

    def get_buffer(self, fs, start, end):
        buffer = np.zeros(self.get_duration(fs))
        for offset, child in self.children:
            start = int(offset*fs)
            end = start + child.get_duration(fs)
            buffer[start:end] += child.get_buffer(fs, 0, end-start)
        return buffer

    def get_duration(self, fs) -> int:
        return max([child.get_duration(fs) + int(offset * fs) for offset, child in self.children])

    def set_sampler(self, sampler: Sampler):
        super().set_sampler(sampler)
        for offset, child in self.children:
            child.set_sampler(OffsetSampler(offset, sampler))
