from typing import List, Tuple

import numpy as np

from SourceState import SourceState
from custom_types import Frames
from sources.Source import Source


class AdditiveSource(Source):
    def __init__(self, children: List[Tuple[float, Source]] = None):
        Source.__init__(self)
        self.children = children if children is not None else []

    def with_source(self, offset: float, source: Source):
        self.children.append((offset, source))
        return self

    def get_buffer(self, fs, start, end):
        buffer = np.zeros(end-start)
        for _, child in self.children:
            buffer += child.sample(fs, self.state.offset, start, end)
        return buffer

    def set_state(self, state: SourceState):
        super().set_state(state)
        for offset, child in self.children:
            child.set_state(self.state.with_offset(offset))

    def get_period(self, fs: Frames) -> Frames:
        # TODO: this is wrong
        return max((offset*fs + child.get_period(fs) for offset, child in self.children))
