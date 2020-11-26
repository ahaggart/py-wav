from custom_types import Frames
from sources.Source import Source


class BufferSource(Source):
    def __init__(self, buf, source_fs: Frames, **kwargs):
        Source.__init__(self)
        self.buf = buf
        self.source_fs = source_fs

    def get_buffer(self, fs: int, start: int, end: int):
        return self.buf[start:end]

    def get_period(self, fs: Frames) -> Frames:
        return len(self.buf) * self.source_fs / fs
