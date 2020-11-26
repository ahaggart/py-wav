from custom_types import Frames
from sources.Source import Source


class BufferSource(Source):
    def __init__(self, buf, source_fs: Frames, **kwargs):
        Source.__init__(self)
        self.create_mapping()
        self.buf = buf
        self.source_fs = source_fs

    def get_buffer(self, fs: int, start: int, end: int):
        return self.buf[start:end]

    def get_duration(self, fs) -> int:
        return int(len(self.buf) * self.source_fs / fs)
