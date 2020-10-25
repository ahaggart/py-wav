import numpy as np
from typing import List, Dict, Tuple

from sources.Source import Source

class AdditiveSource(Source):
    def __init__(self, children: List[Tuple[int, Source]]=None):
        self.children = children if children is not None else []

    def with_source(self, offset: float, source: Source):
        self.children.append((offset, source))
        return self

    def get_buffer(self, fs):
        buffer = np.zeros(int(self.get_duration() * fs))
        for offset, child in self.children:
            child_buffer = child.get_buffer(fs)
            start = int(offset*fs)
            end = start + len(child_buffer)
            buffer[start:end] += child_buffer
        return buffer

    def get_duration(self):
        return max([child.get_duration() + offset for offset, child in self.children])
