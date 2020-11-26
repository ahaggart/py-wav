from typing import List

from SourceState import SourceState
from custom_types import Frames
from sources.Source import Source
from transforms.Transform import Transform


class TransformedSource(Source):
    def __init__(self, child: Source, transforms: List[Transform], **kwargs):
        Source.__init__(self)
        self.child = child
        self.transforms = transforms

    def get_buffer(self, fs, start, end):
        buffer = self.child.get_buffer(fs, start, end)
        for transform in self.transforms:
            buffer = transform.apply(fs, buffer)
        return buffer

    def get_period(self, fs: Frames) -> Frames:
        return self.child.get_period(fs)

    def set_state(self, state: SourceState):
        super().set_state(state)
        self.child.set_state(self.state)
        for transform in self.transforms:
            transform.set_state(self.state)
