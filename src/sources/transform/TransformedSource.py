from typing import List

from sources.Source import Source
from transforms.Transform import Transform


class TransformedSource(Source):
    def __init__(self, child: Source, transforms: List[Transform]):
        Source.__init__(self)
        self.child = child
        self.transforms = transforms

    def get_buffer(self, fs, start, end):
        buffer = self.child.get_buffer(fs)
        for transform in self.transforms:
            transform.apply(buffer)
        return buffer

    def get_duration(self, fs):
        return self.child.get_duration(fs)
