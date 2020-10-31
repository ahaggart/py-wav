from typing import List, Dict

import numpy as np

from samplers.OffsetSampler import OffsetSampler
from samplers.Sampler import Sampler
from sources.Source import Source


class SequentialSource(Source):
    def __init__(self, children: List[Source] = None, **kwargs):
        Source.__init__(self)
        self.create_mapping()
        self.children = children if children is not None else []

    def get_buffer(self, fs, start, end):
        buffer = np.zeros(self.get_duration(fs))
        acc = 0
        for child in self.children:
            start = acc
            acc += child.get_duration(fs)
            end = acc
            buffer[start:end] += child.get_buffer(fs, 0, end-start)
        return buffer

    def get_duration(self, fs) -> int:
        return sum([child.get_duration(fs) for child in self.children])

    def set_sampler(self, sampler: Sampler):
        super().set_sampler(sampler)
        fs = sampler.get_fs()
        acc = 0
        for child in self.children:
            child.set_sampler(OffsetSampler(acc, sampler))
            acc += float(child.get_duration(fs)) / fs
