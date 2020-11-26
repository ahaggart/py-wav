"""Wrapper classes for providing additional indirection.

Wrapper classes may be injected in the source tree to allow for
cross-cutting functionality such as buffer caching to be added while
keeping processing logic simple.
"""
from SourceState import SourceState
from custom_types import Frames
from sources.Source import Source


class SourceWrapper(Source):
    def __init__(self, source: Source):
        Source.__init__(self)
        self.source = source

    def get_buffer(self, fs: Frames, start: Frames, end: Frames):
        return self.source.get_buffer(fs, start, end)

    def set_state(self, state: SourceState):
        super().set_state(state)
        self.source.set_state(state)

    def get_period(self, fs: Frames) -> Frames:
        return self.source.get_period(fs)
