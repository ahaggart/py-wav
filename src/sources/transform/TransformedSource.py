from typing import List

from sources.Source import Source
from transforms.Transform import Transform


class TransformedSource(Source):
    def __init__(self, child: Source, transforms: List[Transform], **kwargs):
        Source.__init__(self)
        self.create_mapping()
        self.child = child
        self.transforms = transforms

    def get_buffer(self, fs, start, end):
        buffer = self.child.get_buffer(fs, start, end)
        for transform in self.transforms:
            buffer = transform.apply(fs, buffer)
        return buffer

    def get_duration(self, fs):
        return self.child.get_duration(fs)
